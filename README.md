# shape-key-mirror-plus

A Blender addon to mirror shape key deltas across the X/Y/Z axis with support for multi-part symmetric geometry.

**Author**: Ciyorie (with GPT support)  
**Blender Version**: 4.2+  

---

## 🧩 Description

**Shape Key Mirror Plus** is a Blender add-on that enables accurate mirroring of shape key deltas across a specified axis. It supports objects with multiple disconnected parts, including those that were split but remain symmetric.

This tool enhances Blender’s native shape key functionality by enabling:

- ✅ Axis-based shape key mirroring
- ✅ Multi-part (disconnected mesh) symmetry handling
- ✅ Support for center-axis (e.g., X=0) self-mapping
- ✅ Automatic direction fallback if no vertices found
- ✅ Customizable tolerance for high-precision mirroring

---

## 🔧 Installation

1. Download the file: `shape_key_mirror_plus_v1.9.zip`
2. Open Blender and go to: **Edit > Preferences > Add-ons**
3. Click **Install**, and select the `.zip` file
4. Enable the add-on: **Shape Key Mirror Plus**
5. You will find it under: **Properties > Object Data > Shape Keys**

---

## 🚀 How to Use

1. Select an object with shape keys
2. Choose a shape key to mirror
3. Set the axis (`X`, `Y`, or `Z`), direction (`Negative` or `Positive`), and tolerance
4. Click the **"Mirror Shape Key"** button

---

## 🎯 Example Use Cases

- Mirroring facial expressions across the X-axis
- Handling symmetric creatures split into left/right objects
- Mirroring deformations on complex, disconnected meshes
- Mirroring blendshapes after geometry edits or cleanup

---

## ⚙️ Features

- Fully procedural symmetry detection
- No dependency on object names or topology
- Auto-detection of mirrored vertex pairs
- Works even after mesh splitting (e.g. `P > Selection`)

---

## 🪪 License

GPL-3.0-or-later
