"""Scroll parts for curriculum.html.

Run:  Blender --background --factory-startup --python scroll.py
Writes assets/scroll/roller.png (RGBA, walnut rod with brass finials),
parchment.jpg (seamless vertical tile) and parchment-edge.png (burnt torn
edge strip with alpha, tiles vertically; the page mirrors it for the right).
"""
import math
from pathlib import Path

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[2] / "public"
OUT = ROOT / "assets" / "scroll"


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    try:
        s.render.engine = "BLENDER_EEVEE_NEXT"
    except TypeError:
        s.render.engine = "BLENDER_EEVEE"
    if hasattr(s.eevee, "taa_render_samples"):
        s.eevee.taa_render_samples = 32
    s.view_settings.view_transform = "Standard"
    w = bpy.data.worlds.new("w")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.01, 0.008, 0.006, 1)
    s.world = w
    return s


def principled(name, color, metallic=0.0, rough=0.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Metallic"].default_value = metallic
    p.inputs["Roughness"].default_value = rough
    return m


def walnut():
    m = principled("walnut", (0.1, 0.05, 0.025), rough=0.38)
    nt = m.node_tree
    p = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.wave_type = "RINGS"
    wave.inputs["Scale"].default_value = 3.0
    wave.inputs["Distortion"].default_value = 6.0
    wave.inputs["Detail"].default_value = 4.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.035, 0.016, 0.008, 1)
    ramp.color_ramp.elements[1].color = (0.19, 0.095, 0.045, 1)
    nt.links.new(tc.outputs["Object"], wave.inputs["Vector"])
    nt.links.new(wave.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], p.inputs["Base Color"])
    return m


def along_x(obj):
    obj.rotation_euler = (0, math.radians(90), 0)


def roller(s):
    wood, brass = walnut(), principled("brass", (0.78, 0.55, 0.22), metallic=1.0, rough=0.28)
    L = 8.0
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=L, vertices=64)
    rod = bpy.context.object
    along_x(rod)
    rod.data.materials.append(wood)
    bpy.ops.object.shade_smooth()
    for side in (-1, 1):
        x = side * L / 2
        parts = [
            ("torus", dict(major_radius=0.17, minor_radius=0.045, location=(x - side * 0.08, 0, 0))),
            ("cyl", dict(radius=0.19, depth=0.12, location=(x + side * 0.02, 0, 0))),
            ("torus", dict(major_radius=0.16, minor_radius=0.035, location=(x + side * 0.11, 0, 0))),
            ("sphere", dict(radius=0.21, location=(x + side * 0.3, 0, 0))),
            ("torus", dict(major_radius=0.08, minor_radius=0.03, location=(x + side * 0.52, 0, 0))),
            ("cone", dict(radius1=0.09, radius2=0.0, depth=0.24, location=(x + side * 0.64, 0, 0))),
        ]
        for kind, kw in parts:
            if kind == "torus":
                bpy.ops.mesh.primitive_torus_add(major_segments=64, minor_segments=16, **kw)
            elif kind == "cyl":
                bpy.ops.mesh.primitive_cylinder_add(vertices=64, **kw)
            elif kind == "sphere":
                bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, **kw)
            else:
                bpy.ops.mesh.primitive_cone_add(vertices=48, **kw)
            o = bpy.context.object
            along_x(o)
            if kind == "cone" and side < 0:
                o.rotation_euler = (0, math.radians(-90), 0)
            o.data.materials.append(brass)
            bpy.ops.object.shade_smooth()

    bpy.ops.object.light_add(type="AREA", location=(-2, -4, 4))
    key = bpy.context.object
    key.data.energy, key.data.size, key.data.color = 900, 6, (1.0, 0.86, 0.68)
    key.rotation_euler = (math.radians(50), 0, math.radians(-20))
    bpy.ops.object.light_add(type="AREA", location=(2, 4, 2))
    rim = bpy.context.object
    rim.data.energy, rim.data.size, rim.data.color = 500, 8, (1.0, 0.5, 0.35)
    rim.rotation_euler = (math.radians(-60), 0, math.radians(180))

    bpy.ops.object.camera_add(location=(0, -10, 0), rotation=(math.radians(90), 0, 0))
    cam = bpy.context.object
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = L + 1.6
    s.camera = cam
    s.render.resolution_x, s.render.resolution_y = 1800, 150
    s.render.film_transparent = True
    s.render.image_settings.file_format = "PNG"
    s.render.image_settings.color_mode = "RGBA"
    s.render.image_settings.compression = 90
    s.render.filepath = str(OUT / "roller.png")
    bpy.ops.render.render(write_still=True)


def parchment(s):
    """Flat emission plane, so the render is exactly the procedural colour."""
    bpy.ops.mesh.primitive_plane_add(size=1)
    plane = bpy.context.object
    m = bpy.data.materials.new("parchment")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    tc = nt.nodes.new("ShaderNodeTexCoord")

    def tex(kind, **inputs):
        t = nt.nodes.new(kind)
        for k, v in inputs.items():
            t.inputs[k].default_value = v
        nt.links.new(tc.outputs["Object"], t.inputs["Vector"])
        return t

    blotch = tex("ShaderNodeTexNoise", Scale=3.0, Detail=8.0, Roughness=0.62)
    fibre = tex("ShaderNodeTexNoise", Scale=60.0, Detail=4.0, Roughness=0.7)
    mp = nt.nodes.new("ShaderNodeMapping")  # stretch fibres along the scroll
    mp.inputs["Scale"].default_value = (5.0, 1.0, 0.25)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], fibre.inputs["Vector"])
    stain = tex("ShaderNodeTexVoronoi", Scale=4.0)
    stain.feature = "SMOOTH_F1"

    base = nt.nodes.new("ShaderNodeValToRGB")
    base.color_ramp.elements[0].color = (0.62, 0.48, 0.3, 1)
    base.color_ramp.elements[1].color = (0.9, 0.82, 0.64, 1)
    base.color_ramp.elements[0].position, base.color_ramp.elements[1].position = 0.3, 0.7
    nt.links.new(blotch.outputs["Fac"], base.inputs["Fac"])

    fmix = nt.nodes.new("ShaderNodeMix")
    fmix.data_type, fmix.blend_type = "RGBA", "MULTIPLY"
    fmix.inputs["Factor"].default_value = 0.22
    nt.links.new(base.outputs["Color"], fmix.inputs["A"])
    nt.links.new(fibre.outputs["Color"], fmix.inputs["B"])

    sramp = nt.nodes.new("ShaderNodeValToRGB")  # tea-stain rings
    sramp.color_ramp.elements[0].color = (0.55, 0.36, 0.18, 1)
    sramp.color_ramp.elements[1].color = (1, 1, 1, 1)
    sramp.color_ramp.elements[0].position, sramp.color_ramp.elements[1].position = 0.05, 0.22
    nt.links.new(stain.outputs["Distance"], sramp.inputs["Fac"])
    smix = nt.nodes.new("ShaderNodeMix")
    smix.data_type, smix.blend_type = "RGBA", "MULTIPLY"
    smix.inputs["Factor"].default_value = 0.35
    nt.links.new(fmix.outputs["Result"], smix.inputs["A"])
    nt.links.new(sramp.outputs["Color"], smix.inputs["B"])

    nt.links.new(smix.outputs["Result"], em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    plane.data.materials.append(m)

    bpy.ops.object.camera_add(location=(0, 0, 5))
    cam = bpy.context.object
    cam.data.type, cam.data.ortho_scale = "ORTHO", 1.0
    s.camera = cam
    s.render.resolution_x = s.render.resolution_y = 1024
    s.render.film_transparent = False
    s.render.image_settings.file_format = "PNG"
    s.render.image_settings.color_mode = "RGB"
    raw = OUT / "parchment-raw.png"
    s.render.filepath = str(raw)
    bpy.ops.render.render(write_still=True)

    # Make it tile vertically: blend each row with the row half a tile away,
    # weighted so the top and bottom edges come from the same rows.
    img = bpy.data.images.load(str(raw))
    w, h = img.size
    px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
    rolled = np.roll(px, h // 2, axis=0)
    y = np.abs(np.linspace(-1, 1, h))[:, None, None]
    weight = np.clip((y - 0.55) / 0.45, 0, 1)
    tile = px * (1 - weight) + rolled * weight
    out_img = bpy.data.images.new("parchment", w, h)
    out_img.pixels[:] = tile.ravel()
    s.render.image_settings.file_format = "JPEG"
    s.render.image_settings.quality = 82
    out_img.save_render(filepath=str(OUT / "parchment.jpg"), scene=s)
    raw.unlink()


def edge():
    """Burnt, torn left edge: periodic in y so it tiles."""
    w, h = 64, 1024
    y = np.arange(h) / h * 2 * np.pi
    rng = np.random.default_rng(3)
    tear = 18 + sum(rng.uniform(1.5, 4) / k * np.sin(k * y + rng.uniform(0, 6.3)) for k in (1, 3, 5, 9, 17, 31, 47))
    x = np.arange(w)[None, :]
    d = x - tear[:, None]                                # <0 outside the paper
    alpha = np.clip(d / 1.5 + 1, 0, 1)                   # torn edge
    char = np.clip(1 - d / 22, 0, 1) ** 1.6              # scorch fading into the sheet
    rgb = np.stack([0.12 + 0.2 * (1 - char), 0.06 + 0.12 * (1 - char), 0.02 + 0.05 * (1 - char)], -1)
    a = alpha * np.clip(char * 1.15, 0, 1)
    px = np.concatenate([rgb, a[..., None]], -1)[::-1]   # Blender images start at the bottom row
    img = bpy.data.images.new("edge", w, h, alpha=True)
    img.pixels[:] = px.astype(np.float32).ravel()
    img.filepath_raw = str(OUT / "parchment-edge.png")
    img.file_format = "PNG"
    img.save()


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    roller(reset())
    parchment(reset())
    edge()
    for f in sorted(OUT.iterdir()):
        print("OUT", f.name, f.stat().st_size // 1024, "KB")
