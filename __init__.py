# SPDX-License-Identifier: GPL-3.0-or-later

bl_info = {
    "name": "Shape Key Mirror Plus",
    "author": "Ciyorie (with GPT support)",
    "version": (1, 8),
    "blender": (4, 2, 0),
    "location": "Properties > Object Data > Shape Key Mirror Plus",
    "description": "Mirror shape key deltas across a selected axis, with support for multi-part symmetric meshes and split objects.",
    "category": "Object",
}

from . import shape_key_mirror_plus

def register():
    shape_key_mirror_plus.register()

def unregister():
    shape_key_mirror_plus.unregister()
