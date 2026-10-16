"""Seamless atmospheric background loops, one per issue.

Run:  Blender --background --python bg_loops.py -- <issue 1-5|all> [test]
Every moving thing is a periodic function of the frame (drivers using
sin/cos of frame/N*2pi), so frame N == frame 0 and frames 1..N loop cleanly.
Writes assets/video/bg-{n}.mp4 and bg-{n}.jpg (or debug/bg-{n}-f*.png in test mode).
"""
import math
import random
import sys
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[2] / "public"
VIDEO, DEBUG = ROOT / "assets" / "video", ROOT / "assets" / "debug"
N = 144  # 6 s at 24 fps
W, H = 1280, 720

PALETTES = {  # haze colour, key light colour, light energy, shafts?
    1: dict(haze=(0.20, 0.09, 0.05), light=(1.0, 0.45, 0.22), energy=14000, shafts=False, density=0.55),
    2: dict(haze=(0.22, 0.03, 0.04), light=(1.0, 0.16, 0.12), energy=11000, shafts=True, density=0.6),
    3: dict(haze=(0.05, 0.16, 0.17), light=(0.45, 0.95, 0.9), energy=12000, shafts=True, density=0.45),
    4: dict(haze=(0.20, 0.13, 0.04), light=(1.0, 0.72, 0.3), energy=13000, shafts=False, density=0.5),
    5: dict(haze=(0.03, 0.07, 0.16), light=(0.45, 0.65, 1.0), energy=9000, shafts=True, density=0.5),
    6: dict(haze=(0.14, 0.02, 0.02), light=(1.0, 0.12, 0.1), energy=12000, shafts=True, density=0.55),
}


def periodic(obj, path, index, expr):
    fc = obj.driver_add(path, index)
    fc.driver.type = "SCRIPTED"
    fc.driver.expression = expr.replace("T", f"(frame/{N}*2*pi)")


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    try:
        s.render.engine = "BLENDER_EEVEE_NEXT"
    except TypeError:
        s.render.engine = "BLENDER_EEVEE"
    s.render.resolution_x, s.render.resolution_y = W, H
    s.render.fps = 24
    s.frame_start, s.frame_end = 1, N
    ee = s.eevee
    for k, v in dict(taa_render_samples=16, volumetric_tile_size="8", volumetric_samples=48,
                     use_volumetric_shadows=True, volumetric_end=40.0).items():
        if hasattr(ee, k):
            setattr(ee, k, v)
    s.view_settings.view_transform = "AgX" if "AgX" in [i.identifier for i in s.view_settings.bl_rna.properties["view_transform"].enum_items] else "Filmic"
    s.view_settings.look = "None"
    s.view_settings.exposure = -0.4
    return s


def world(s):
    w = bpy.data.worlds.new("void")
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.002, 0.002, 0.002, 1)
    s.world = w


def haze(pal):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 3, 0))
    box = bpy.context.object
    box.scale = (30, 10, 20)
    box.name = "Haze"
    m = bpy.data.materials.new("haze")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    vol = nt.nodes.new("ShaderNodeVolumePrincipled")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.noise_dimensions = "3D"
    nz.inputs["Scale"].default_value = 5.5
    nz.inputs["Detail"].default_value = 6
    nz.inputs["Roughness"].default_value = 0.6
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.47
    ramp.color_ramp.elements[1].position = 0.62
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = pal["density"] * 0.9
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], mul.inputs[0])
    nt.links.new(mul.outputs[0], vol.inputs["Density"])
    vol.inputs["Color"].default_value = (*pal["haze"], 1)
    vol.inputs["Anisotropy"].default_value = 0.55
    nt.links.new(vol.outputs[0], out.inputs["Volume"])
    m.node_tree.nodes  # keep reference
    box.data.materials.append(m)
    # Drift the noise around a closed circle in texture space: perfect loop.
    loc = mp.inputs["Location"]
    for i, expr in enumerate(("cos(T)*0.06", "sin(T)*0.06", "sin(T)*0.025")):
        fc = m.node_tree.driver_add(f'nodes["{mp.name}"].inputs[1].default_value', i)
        fc.driver.type = "SCRIPTED"
        fc.driver.expression = expr.replace("T", f"(frame/{N}*2*pi)")
    return box


def lights(pal):
    bpy.ops.object.light_add(type="SPOT", location=(-3, 9, 10))
    key = bpy.context.object
    key.data.energy = pal["energy"]
    key.data.color = pal["light"]
    key.data.spot_size = math.radians(55)
    key.data.spot_blend = 0.8
    key.data.shadow_soft_size = 0.6
    aim = bpy.data.objects.new("aim", None)
    bpy.context.collection.objects.link(aim)
    aim.location = (1, 0, -1)
    c = key.constraints.new("TRACK_TO")
    c.target = aim
    periodic(key, "location", 0, "-3+sin(T)*0.35")
    periodic(key.data, "energy", -1, f"{pal['energy']}*(0.92+0.08*sin(T*3))")

    bpy.ops.object.light_add(type="POINT", location=(0, -2, -3))
    fill = bpy.context.object
    fill.data.energy = 40
    fill.data.color = pal["light"]


def shafts():
    """A row of tall slats between the key light and the haze: light comes through in beams."""
    m = bpy.data.materials.new("slat")
    m.diffuse_color = (0, 0, 0, 1)
    for i in range(10):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(-6.2 + i * 0.75, 7.5, 7.6))
        o = bpy.context.object
        o.scale = (0.38, 5, 0.15)
        o.data.materials.append(m)
        o.visible_camera = False


def dust(pal, count=70):
    random.seed(7)
    me = bpy.data.meshes.new("dust_pts")
    me.from_pydata([(random.uniform(-9, 9), random.uniform(-1, 6), random.uniform(-5, 5)) for _ in range(count)], [], [])
    ob = bpy.data.objects.new("Dust", me)
    bpy.context.collection.objects.link(ob)

    mat = bpy.data.materials.new("mote")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*[min(1, c * 0.9 + 0.1) for c in pal["light"]], 1)
    em.inputs["Strength"].default_value = 0.6
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(em.outputs[0], out.inputs["Surface"])

    gn = ob.modifiers.new("drift", "NODES")
    g = bpy.data.node_groups.new("drift", "GeometryNodeTree")
    gn.node_group = g
    g.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    g.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    n = g.nodes
    gi, go = n.new("NodeGroupInput"), n.new("NodeGroupOutput")
    st = n.new("GeometryNodeInputSceneTime")
    tmul = n.new("ShaderNodeMath"); tmul.operation = "MULTIPLY"; tmul.inputs[1].default_value = 2 * math.pi / N
    g.links.new(st.outputs["Frame"], tmul.inputs[0])

    def phase_wave(seed, amp, fn="SINE", speed=1):
        rnd = n.new("FunctionNodeRandomValue"); rnd.data_type = "FLOAT"
        rnd.inputs["Min"].default_value, rnd.inputs["Max"].default_value = 0, 2 * math.pi
        rnd.inputs["Seed"].default_value = seed
        sp = n.new("ShaderNodeMath"); sp.operation = "MULTIPLY"; sp.inputs[1].default_value = speed
        g.links.new(tmul.outputs[0], sp.inputs[0])
        add = n.new("ShaderNodeMath"); add.operation = "ADD"
        g.links.new(sp.outputs[0], add.inputs[0]); g.links.new(rnd.outputs["Value"], add.inputs[1])
        s = n.new("ShaderNodeMath"); s.operation = fn
        g.links.new(add.outputs[0], s.inputs[0])
        a = n.new("ShaderNodeMath"); a.operation = "MULTIPLY"; a.inputs[1].default_value = amp
        g.links.new(s.outputs[0], a.inputs[0])
        return a.outputs[0]

    comb = n.new("ShaderNodeCombineXYZ")
    g.links.new(phase_wave(1, 0.6), comb.inputs[0])
    g.links.new(phase_wave(2, 0.25, "COSINE"), comb.inputs[1])
    g.links.new(phase_wave(3, 0.8, "SINE"), comb.inputs[2])
    sp = n.new("GeometryNodeSetPosition")
    g.links.new(gi.outputs[0], sp.inputs["Geometry"])
    g.links.new(comb.outputs[0], sp.inputs["Offset"])
    ico = n.new("GeometryNodeMeshIcoSphere"); ico.inputs["Radius"].default_value = 0.024; ico.inputs["Subdivisions"].default_value = 1
    rs = n.new("FunctionNodeRandomValue"); rs.data_type = "FLOAT"
    rs.inputs["Min"].default_value, rs.inputs["Max"].default_value = 0.4, 1.8
    iop = n.new("GeometryNodeInstanceOnPoints")
    g.links.new(sp.outputs[0], iop.inputs["Points"])
    g.links.new(ico.outputs["Mesh"], iop.inputs["Instance"])
    g.links.new(rs.outputs["Value"], iop.inputs["Scale"])
    sm = n.new("GeometryNodeSetMaterial"); sm.inputs["Material"].default_value = mat
    g.links.new(iop.outputs[0], sm.inputs["Geometry"])
    g.links.new(sm.outputs[0], go.inputs[0])


def camera():
    bpy.ops.object.camera_add(location=(0, -12, 0), rotation=(math.radians(90), 0, 0))
    cam = bpy.context.object
    cam.data.lens = 32
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = 30
    cam.data.dof.aperture_fstop = 0.6
    periodic(cam, "location", 0, "sin(T)*0.25")
    periodic(cam, "location", 2, "cos(T)*0.12")
    bpy.context.scene.camera = cam


def output(s, n, test):
    if test:
        for f in (1, N // 3, N):
            s.frame_set(f)
            s.render.image_settings.file_format = "PNG"
            s.render.filepath = str(DEBUG / f"bg-{n}-f{f:03d}.png")
            bpy.ops.render.render(write_still=True)
        return
    s.frame_set(1)
    s.render.image_settings.file_format = "JPEG"
    s.render.image_settings.quality = 78
    s.render.filepath = str(VIDEO / f"bg-{n}.jpg")
    bpy.ops.render.render(write_still=True)
    ims = s.render.image_settings
    if hasattr(ims, "media_type"):
        ims.media_type = "VIDEO"
    ims.file_format = "FFMPEG"
    ff = s.render.ffmpeg
    ff.format, ff.codec = "MPEG4", "H264"
    ff.constant_rate_factor = "LOW"
    ff.ffmpeg_preset = "GOOD"
    ff.gopsize = 24
    s.render.filepath = str(VIDEO / f"bg-{n}.mp4")
    bpy.ops.render.render(animation=True)


def build(n, test):
    pal = PALETTES[n]
    s = reset()
    world(s)
    haze(pal)
    lights(pal)
    if pal["shafts"]:
        shafts()
    dust(pal)
    camera()
    output(s, n, test)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["all"]
    which = range(1, 7) if args[0] == "all" else [int(args[0])]
    VIDEO.mkdir(parents=True, exist_ok=True)
    DEBUG.mkdir(parents=True, exist_ok=True)
    for n in which:
        build(n, "test" in args)
