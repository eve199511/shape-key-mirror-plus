
bl_info = {
    "name": "Shape Key Mirror Plus",
    "author": "Ciyorie (with GPT support)",
    "version": (1, 9),
    "blender": (4, 2, 0),
    "location": "Properties > Object Data > Shape Keys",
    "description": "Mirror and swap shape key deltas with robust symmetry detection.",
    "category": "Object",
}

import bpy
import bmesh
from mathutils import Vector

def find_mirror_map(obj, axis='X', direction='NEGATIVE', tolerance=0.0001):
    axis_index = {'X': 0, 'Y': 1, 'Z': 2}[axis]
    mesh = obj.data
    coords = [v.co.copy() for v in mesh.vertices]

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()

    visited = set()
    components = []

    for v in bm.verts:
        if v.index in visited:
            continue
        stack = [v]
        comp = []
        while stack:
            curr = stack.pop()
            if curr.index in visited:
                continue
            visited.add(curr.index)
            comp.append(curr.index)
            for e in curr.link_edges:
                n = e.other_vert(curr)
                if n.index not in visited:
                    stack.append(n)
        components.append(comp)
    bm.free()

    mirror_map = {}
    used = set()

    for comp in components:
        for i in comp:
            co = coords[i]
            if direction == 'NEGATIVE' and co[axis_index] > -tolerance:
                continue
            if direction == 'POSITIVE' and co[axis_index] < tolerance:
                continue

            mirrored = co.copy()
            mirrored[axis_index] *= -1

            best_j, best_d = None, tolerance
            for j in comp:
                if j == i or j in used:
                    continue
                dist = (mirrored - coords[j]).length
                if dist < best_d:
                    best_j, best_d = j, dist

            if best_j is None:
                for j, test_co in enumerate(coords):
                    if j == i or j in used:
                        continue
                    dist = (mirrored - test_co).length
                    if dist < best_d:
                        best_j, best_d = j, dist

            if best_j is not None:
                mirror_map[i] = best_j
                used.add(best_j)

    for i, co in enumerate(coords):
        if abs(co[axis_index]) <= tolerance:
            mirror_map[i] = i

    return mirror_map

def is_symmetric(obj, base_key, axis='X', tolerance=0.0001):
    coords = [v.co for v in base_key.data]
    axis_idx = {'X': 0, 'Y': 1, 'Z': 2}[axis]

    mirror_map = find_mirror_map(obj, axis, 'NEGATIVE', tolerance)

    for i, j in mirror_map.items():
        if i == j:
            continue
        vi = coords[i]
        vj = coords[j]
        delta = vi.copy()
        delta[axis_idx] *= -1
        if (delta - vj).length > tolerance:
            return False
    return True

class OBJECT_OT_shape_key_mirror(bpy.types.Operator):
    bl_idname = "object.shape_key_mirror_plus"
    bl_label = "Mirror Shape Key (Symmetric)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        props = context.scene.shape_key_mirror_props
        sk_name = props.shape_key_enum
        axis = props.axis
        direction = props.direction
        tolerance = props.tolerance

        if not obj or not obj.data.shape_keys:
            self.report({'ERROR'}, "No shape keys found.")
            return {'CANCELLED'}

        key_blocks = obj.data.shape_keys.key_blocks
        if sk_name not in key_blocks:
            self.report({'ERROR'}, f"Shape key '{sk_name}' not found.")
            return {'CANCELLED'}

        target = key_blocks[sk_name]
        reference = target.relative_key
        if not reference:
            self.report({'ERROR'}, f"Shape key '{sk_name}' has no relative key.")
            return {'CANCELLED'}

        if not is_symmetric(obj, reference, axis, tolerance):
            self.report({'ERROR'}, f"Reference shape key '{reference.name}' is not symmetric on {axis}-axis.")
            return {'CANCELLED'}

        mirror_map = find_mirror_map(obj, axis, direction, tolerance)
        axis_idx = {'X': 0, 'Y': 1, 'Z': 2}[axis]

        for src, dst in mirror_map.items():
            try:
                ref_src = reference.data[src].co
                ref_dst = reference.data[dst].co
                delta = target.data[src].co - ref_src

                mirrored_delta = delta.copy()
                mirrored_delta[axis_idx] *= -1
                new_co = ref_dst + mirrored_delta

                if abs(ref_dst[axis_idx]) <= tolerance:
                    new_co[axis_idx] = ref_dst[axis_idx]

                target.data[dst].co = new_co
            except IndexError:
                continue

        return {'FINISHED'}

class OBJECT_OT_shape_key_swap(bpy.types.Operator):
    bl_idname = "object.shape_key_mirror_swap"
    bl_label = "Swap Shape Key Mirror"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        props = context.scene.shape_key_mirror_props
        sk_name = props.shape_key_enum
        axis = props.axis
        direction = props.direction
        tolerance = props.tolerance

        if not obj or not obj.data.shape_keys:
            self.report({'ERROR'}, "No shape keys found.")
            return {'CANCELLED'}

        key_blocks = obj.data.shape_keys.key_blocks
        if sk_name not in key_blocks:
            self.report({'ERROR'}, f"Shape key '{sk_name}' not found.")
            return {'CANCELLED'}

        target = key_blocks[sk_name]
        reference = target.relative_key
        if not reference:
            self.report({'ERROR'}, f"Shape key '{sk_name}' has no relative key.")
            return {'CANCELLED'}

        if not is_symmetric(obj, reference, axis, tolerance):
            self.report({'ERROR'}, f"Reference shape key '{reference.name}' is not symmetric.")
            return {'CANCELLED'}

        mirror_map = find_mirror_map(obj, axis, direction, tolerance)
        axis_idx = {'X': 0, 'Y': 1, 'Z': 2}[axis]
        swapped = set()

        for src, dst in mirror_map.items():
            if (dst, src) in swapped:
                continue
            try:
                ref_src = reference.data[src].co
                ref_dst = reference.data[dst].co
                delta_src = target.data[src].co - ref_src
                delta_dst = target.data[dst].co - ref_dst

                delta_src[axis_idx] *= -1
                delta_dst[axis_idx] *= -1

                target.data[src].co = ref_src + delta_dst
                target.data[dst].co = ref_dst + delta_src

                swapped.add((src, dst))
            except IndexError:
                continue

        return {'FINISHED'}

class ShapeKeyMirrorProperties(bpy.types.PropertyGroup):
    def get_shape_keys(self, context):
        obj = context.object
        if obj and obj.data.shape_keys:
            return [(kb.name, kb.name, "") for kb in obj.data.shape_keys.key_blocks]
        return []

    shape_key_enum: bpy.props.EnumProperty(name="Shape Key", items=get_shape_keys)
    axis: bpy.props.EnumProperty(name="Axis", items=[('X', "X", ""), ('Y', "Y", ""), ('Z', "Z", "")], default='X')
    direction: bpy.props.EnumProperty(name="Direction", items=[('NEGATIVE', "- → +", ""), ('POSITIVE', "+ → -", "")], default='NEGATIVE')
    tolerance: bpy.props.FloatProperty(name="Tolerance", default=0.0001, min=0.0, precision=6)

class OBJECT_PT_shape_key_mirror_panel(bpy.types.Panel):
    bl_label = "Shape Key Mirror Plus"
    bl_idname = "OBJECT_PT_shape_key_mirror_plus"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    def draw(self, context):
        layout = self.layout
        props = context.scene.shape_key_mirror_props

        layout.prop(props, "shape_key_enum")
        layout.prop(props, "axis")
        layout.prop(props, "direction", expand=True)
        layout.prop(props, "tolerance")
        layout.operator("object.shape_key_mirror_plus", text="Symmetrize Shape Key")
        layout.operator("object.shape_key_mirror_swap", text="Mirror Shape Key")

class OBJECT_PT_shape_key_mirror_panel(bpy.types.Panel):
    bl_label = "Shape Key Mirror Plus"
    bl_idname = "OBJECT_PT_shape_key_mirror_plus"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"
    bl_parent_id = "DATA_PT_shape_keys"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        props = context.scene.shape_key_mirror_props

        box = layout.box()
        box.label(text="Mirror Plus Tools", icon='MOD_MIRROR')

        row = box.row()
        row.prop(props, "shape_key_enum", text="Key")

        row = box.row(align=True)
        row.prop(props, "axis", expand=True)
        row.prop(props, "tolerance", text="Tolerance")

        row = box.row(align=True)
        row.prop(props, "direction", expand=True)
        row.operator("object.shape_key_mirror_plus", text="Symmetrize", icon='ARROW_LEFTRIGHT')

        row = box.row()
        row.operator("object.shape_key_mirror_swap", text="Mirror Shape Key", icon='FILE_REFRESH')

classes = (
    OBJECT_OT_shape_key_mirror,
    OBJECT_OT_shape_key_swap,
    ShapeKeyMirrorProperties,
    OBJECT_PT_shape_key_mirror_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.shape_key_mirror_props = bpy.props.PointerProperty(type=ShapeKeyMirrorProperties)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.shape_key_mirror_props

if __name__ == "__main__":
    register()
