"""The eye-pyramid: obsidian double pyramid, one eye, a halo of rays.

Run:  Blender --background --python pyramid.py
Writes assets/models/pyramid.glb with nodes "Lid" (eye, scaled to blink/open),
"Iris" (moved by the page toward the cursor) and "Halo", plus one animation
"Awaken" (eye opens, halo grows). Front is Blender -Y, which glTF exports as +Z.
"""
import math
from pathlib import Path

import bmesh
import bpy

ROOT = Path(__file__).resolve().parents[2] / "public"
OUT = ROOT / "assets" / "models" / "pyramid.glb"
A, H = 0.92, 1.0  # half-width of the base square (front ridge at y=-A), half-height


def material(name, color=(0, 0, 0), emit=None, strength=1.0, metallic=0.0, rough=0.5, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Metallic"].default_value = metallic
    p.inputs["Roughness"].default_value = rough
    if coat:
        p.inputs["Coat Weight"].default_value = coat
        p.inputs["Coat Roughness"].default_value = 0.08
    if emit:
        p.inputs["Emission Color"].default_value = (*emit, 1)
        p.inputs["Emission Strength"].default_value = strength
    return m


def mesh_object(name, build, mat, parent=None, location=(0, 0, 0)):
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    build(bm)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat)
    ob.parent = parent
    ob.location = location
    return ob


def empty(name, parent=None, location=(0, 0, 0)):
    ob = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(ob)
    ob.parent = parent
    ob.location = location
    return ob


def disc(r, segs=48):
    """A disc in the XZ plane facing -Y."""
    def build(bm):
        c = bm.verts.new((0, 0, 0))
        ring = [bm.verts.new((r * math.cos(t), 0, r * math.sin(t))) for t in (i / segs * 2 * math.pi for i in range(segs))]
        for i in range(segs):
            bm.faces.new((c, ring[(i + 1) % segs], ring[i]))
    return build


def body(bm):
    top, bot = bm.verts.new((0, 0, H)), bm.verts.new((0, 0, -H))
    base = [bm.verts.new(v) for v in ((A, -A, 0), (-A, -A, 0), (-A, A, 0), (A, A, 0))]
    for i in range(4):
        p, q = base[i], base[(i + 1) % 4]
        bm.faces.new((top, p, q))
        bm.faces.new((bot, q, p))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)


def almond(bm, w=0.27, h=0.13, n=28):
    pts = []
    for i in range(n + 1):  # upper lid then lower lid, quadratic arcs
        t = i / n
        pts.append(((2 * t - 1) * w, 0, 4 * h * t * (1 - t)))
    for i in range(n - 1, 0, -1):
        t = i / n
        pts.append(((2 * t - 1) * w, 0, -4 * h * t * (1 - t)))
    c = bm.verts.new((0, 0, 0))
    vs = [bm.verts.new(p) for p in pts]
    for i in range(len(vs)):
        bm.faces.new((c, vs[(i + 1) % len(vs)], vs[i]))


def rays(bm, count=56):
    for i in range(count):
        long = i % 2 == 0
        length, width = (1.25, 0.016) if long else (0.7, 0.01)
        r0, ang = 1.18, i / count * 2 * math.pi
        d = (math.cos(ang), math.sin(ang))
        n = (-d[1], d[0])
        quad = []
        for along, side in ((r0, -1), (r0, 1), (r0 + length, 1), (r0 + length, -1)):
            x = d[0] * along + n[0] * side * width / 2
            z = d[1] * along + n[1] * side * width / 2
            quad.append(bm.verts.new((x, 0, z)))
        bm.faces.new(quad)


def keys(ob, path, frames):
    for f, v in frames:
        setattr(ob, path, v)
        ob.keyframe_insert(path, frame=f)
    ad = ob.animation_data
    track = ad.nla_tracks.new()
    track.name = "Awaken"
    track.strips.new("Awaken", 1, ad.action)
    ad.action = None


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.frame_start, bpy.context.scene.frame_end = 1, 72
    bpy.context.scene.render.fps = 24

    obsidian = material("Obsidian", color=(0.006, 0.006, 0.008), metallic=0.2, rough=0.2, coat=0.8)
    pyr = mesh_object("Pyramid", body, obsidian)
    bev = pyr.modifiers.new("bevel", "BEVEL")
    bev.width, bev.segments, bev.limit_method = 0.014, 2, "ANGLE"

    lid = empty("Lid", location=(0, -A - 0.012, 0))
    mesh_object("EyeWhite", almond, material("EyeWhite", emit=(0.95, 0.93, 0.86), strength=1.0), parent=lid)
    iris = empty("Iris", parent=lid, location=(0, -0.002, 0))
    mesh_object("Ring", disc(0.095), material("Ring", emit=(0.75, 0.55, 0.25), strength=0.9), parent=iris)
    mesh_object("IrisDisc", disc(0.078), material("IrisBlue", emit=(0.06, 0.13, 0.24), strength=1.0), parent=iris, location=(0, -0.001, 0))
    mesh_object("Pupil", disc(0.034), material("Pupil", color=(0, 0, 0)), parent=iris, location=(0, -0.002, 0))
    mesh_object("Glint", disc(0.012, 16), material("Glint", emit=(1, 1, 1), strength=2.0), parent=iris, location=(0.026, -0.003, 0.026))

    halo = mesh_object("Halo", rays, material("HaloGold", emit=(1.0, 0.85, 0.55), strength=2.2), location=(0, 0.6, 0))

    keys(lid, "scale", [(1, (1, 1, 0.03)), (28, (1, 1, 0.03)), (64, (1, 1, 1.0))])
    keys(halo, "scale", [(1, (0.2, 0.2, 0.2)), (72, (1, 1, 1))])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(OUT), export_format="GLB", export_apply=True, export_yup=True,
        export_animations=True, export_animation_mode="NLA_TRACKS",
        export_cameras=False, export_lights=False,
    )

    # Re-import as a check.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(OUT))
    print("OBJECTS", sorted(o.name for o in bpy.data.objects))
    print("ACTIONS", [a.name for a in bpy.data.actions])
    print("SIZE_KB", OUT.stat().st_size // 1024)


if __name__ == "__main__":
    main()
