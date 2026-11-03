"""FTC v2 facility kit, built headless in Blender (5.1+). One script makes both 3D deliverables:

  - the GLB for the live three.js cutaway (geometry only; the page colours it from the design tokens)
  - the fly-through film for the scroll section (EEVEE frames + per-step posters)

Run from the project root:
  Blender -b -P tools/blender/facility.py -- --glb src/models/facility.glb
  Blender -b -P tools/blender/facility.py -- --preview /tmp/prev          # key frames, low samples
  Blender -b -P tools/blender/facility.py -- --render /tmp/frames [--from 1 --to 270 --step 2 --w 1920 --h 1080]
  Blender -b -P tools/blender/facility.py -- --blend design/3d/ftc-facility.blend

Units are metres, Blender Z-up. The glTF export turns that into three.js Y-up: (x, y, z) -> (x, z, -y).
Every mesh is one (part, role) bucket. `part` is what the visitor clicks (dock, cold, freezer, plant, ahu,
racks, van); `role` says what it is made of, so the page can colour it from the theme.
"""
import bpy, bmesh, math, sys, random
from contextlib import contextmanager
from mathutils import Matrix, Euler

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
def arg(name, default=None): return argv[argv.index(name) + 1] if name in argv else default

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
random.seed(7)

# ---------------------------------------------------------------- geometry buckets
GEO = {}
GM = [Matrix.Identity(4)]  # group transform stack (vehicles, forklift)

def bm_for(part, role):
    k = (part or "shell", role)
    if k not in GEO: GEO[k] = bmesh.new()
    return GEO[k]

def M(loc, size=(1, 1, 1), rot=(0, 0, 0)):
    return (GM[-1] @ Matrix.Translation(loc) @ Euler([math.radians(a) for a in rot]).to_matrix().to_4x4()
            @ Matrix.Diagonal((*size, 1)))

@contextmanager
def group(x, y, z, rz=0):
    GM.append(GM[-1] @ Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(rz), 4, "Z"))
    yield
    GM.pop()

def box(part, role, sx, sy, sz, x, y, z, rot=(0, 0, 0)):
    """Box sized sx*sy*sz, centred on x/y, standing on z."""
    bmesh.ops.create_cube(bm_for(part, role), size=1.0, matrix=M((x, y, z + sz / 2), (sx, sy, sz), rot))

def cyl(part, role, r, h, x, y, z, axis="z", seg=20):
    """Cylinder centred on x/y/z along an axis."""
    rot = {"z": (0, 0, 0), "x": (0, 90, 0), "y": (90, 0, 0)}[axis]
    bmesh.ops.create_cone(bm_for(part, role), cap_ends=True, cap_tris=False, segments=seg,
                          radius1=r, radius2=r, depth=h, matrix=M((x, y, z), (1, 1, 1), rot))

def text(part, role, body, size, x, y, z, rot=(90, 0, 0)):
    cu = bpy.data.curves.new("t", "FONT"); cu.body = body; cu.size = size; cu.extrude = 0.008
    cu.align_x = "CENTER"
    ob = bpy.data.objects.new("t", cu); scene.collection.objects.link(ob)
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    me.transform(M((x, y, z), (1, 1, 1), rot)); bm_for(part, role).from_mesh(me)
    bpy.data.objects.remove(ob); bpy.data.curves.remove(cu); bpy.data.meshes.remove(me)

def panel_wall(part, role, a, b, axis, at, h, t=0.15, openings=(), z=0, w=1.2, gap=0.02):
    """A wall of insulated panels from a to b along `axis` ('x' or 'y') at the other coordinate `at`.
    openings: (start, end, top) spans; panels over an opening only fill the header above it."""
    n = max(1, round((b - a) / w)); pw = (b - a) / n
    for i in range(n):
        c = a + pw * (i + 0.5); z0 = z
        for s, e, top in openings:
            if s - 0.01 <= c <= e + 0.01: z0 = top
        if z0 >= h: continue
        sx, sy = (pw - gap, t) if axis == "x" else (t, pw - gap)
        x, y = (c, at) if axis == "x" else (at, c)
        box(part, role, sx, sy, h - z0, x, y, z0)

def rack_row(part, x0, bays, y, levels, height, depth=1.1, bay=2.7, fill=0.85):
    xs = [x0 + i * bay for i in range(bays + 1)]
    for x in xs:
        for f in (-1, 1): box(part, "upright", 0.1, 0.1, height, x, y + f * depth / 2, 0)
        box(part, "upright", 0.06, depth, 0.06, x, y, height - 0.3)
    for i in range(bays):
        xm = x0 + (i + 0.5) * bay
        for lv in levels:
            if lv > 0:
                for f in (-1, 1): box(part, "beam", bay - 0.1, 0.08, 0.14, xm, y + f * depth / 2, lv - 0.14)
            for k in (-0.62, 0.62):
                if random.random() > fill: continue
                base = lv + (0.0 if lv == 0 else 0.0)
                box(part, "pallet", 1.0, depth - 0.1, 0.14, xm + k, y, base)
                box(part, random.choice(("stock", "stock", "stock2")), 0.96, depth - 0.16,
                    random.uniform(0.9, 1.35), xm + k, y, base + 0.14)

# ---------------------------------------------------------------- building shell (cut away at the front)
box(None, "floor", 38, 24, 0.3, 0, 0, -0.3)
box(None, "yard", 26, 44, 0.3, 31, -6, -1.5)            # truck yard, 1.2 m below the dock floor
box(None, "slab", 0.6, 24, 1.2, 18.7, 0, -1.2)            # dock face
DOCKS = (-8.0, -3.5, 1.0)
panel_wall(None, "clad", -11, 11, "y", -18, 9, 0.2, w=1.0)
panel_wall(None, "clad", -18, 18, "x", 11, 9, 0.2, w=1.0)
panel_wall(None, "clad", -11, 11, "y", 18, 9, 0.2, w=1.0, openings=[(c - 1.6, c + 1.6, 3.4) for c in DOCKS])
for x in range(-18, 19, 6):
    for y in (-11, 11): box(None, "steel", 0.35, 0.35, 9, x, y, 0)
    box(None, "roof", 0.3, 22.4, 0.7, x, 0, 8.6)
for y in (-11, -5.5, 0, 5.5, 11): box(None, "roof", 36.4, 0.16, 0.24, 0, y, 9.3)

# ---------------------------------------------------------------- cold room (0..+5 °C) and freezer (-25 °C)
def room(part, x0, x1, y0, y1, h, t, door_x):
    panel_wall(part, "panel", x0, x1, "x", y1, h, t)
    panel_wall(part, "panel", y0, y1, "y", x0, h, t)
    panel_wall(part, "panel", y0, y1, "y", x1, h, t)
    panel_wall(part, "panel", x0, x1, "x", y0, h, t, openings=[(door_x - 1.25, door_x + 1.25, 3.0)])
    box(part, "panelfloor", x1 - x0 - 0.3, y1 - y0 - 0.3, 0.06, (x0 + x1) / 2, (y0 + y1) / 2, 0)
    # sliding door, parked open beside the opening, with its rail
    box(part, "door", 2.7, 0.14, 3.1, door_x + 2.7, y0 - 0.16, 0)
    box(part, "steel", 5.6, 0.12, 0.14, door_x + 1.4, y0 - 0.16, 3.12)
    for k in (-1.3, 1.3): box(part, "accent", 0.08, 0.2, 3.0, door_x + k, y0, 0)
    box(part, "accent", 2.68, 0.2, 0.08, door_x, y0, 3.0)
    for i in range(8): box(part, "curtain", 0.3, 0.02, 2.95, door_x - 1.05 + i * 0.3, y0 + 0.1, 0.02)
    # roof-hung evaporators with three fans each
    for ex in (x0 + (x1 - x0) * 0.28, x0 + (x1 - x0) * 0.72):
        box(part, "unit", 2.6, 0.8, 0.66, ex, y1 - 0.65, h - 1.3)
        for f in (-0.8, 0, 0.8): cyl(part, "fan", 0.24, 0.05, ex + f, y1 - 1.06, h - 0.97, "y")
        box(part, "steel", 0.05, 0.05, 0.64, ex - 1.1, y1 - 0.65, h - 0.64); box(part, "steel", 0.05, 0.05, 0.64, ex + 1.1, y1 - 0.65, h - 0.64)

room("cold", -16, -4, 1, 10, 6, 0.15, -10)
room("freezer", -3, 6, 1, 10, 6, 0.2, 1.5)
rack_row("cold", -15.4, 4, 4.3, (0, 1.9), 4.0)
rack_row("cold", -15.4, 4, 6.9, (0, 1.9), 4.0)
rack_row("freezer", -2.55, 3, 5.6, (0, 1.9), 4.0)

# ---------------------------------------------------------------- loading dock
for i, c in enumerate(DOCKS):
    open_ = c == -3.5
    box("dock", "plate", 2.0, 2.3, 0.06, 17.0, c, 0)                          # leveller
    for f in (-1, 1): box("dock", "accent", 2.0, 0.08, 0.07, 17.0, c + f * 1.15, 0)
    for f in (-1, 1): box("dock", "rubber", 0.55, 0.5, 3.7, 18.48, c + f * 1.75, -0.25)  # shelter pads
    box("dock", "rubber", 0.55, 4.0, 0.6, 18.48, c, 3.15)
    for f in (-0.9, 0.9): box("dock", "rubber", 0.25, 0.35, 0.45, 19.1, c + f, -0.75)    # bumpers
    if open_:   # sectional door rolled up into its track
        box("dock", "door", 3.3, 3.1, 0.08, 16.3, c, 3.55)
        for f in (-1, 1): box("dock", "steel", 3.6, 0.06, 0.08, 16.3, c + f * 1.6, 3.5)
    else:
        box("dock", "door", 0.08, 3.1, 3.4, 17.85, c, 0)
        for k in range(1, 7): box("dock", "trim", 0.1, 3.12, 0.04, 17.82, c, k * 0.5)
        box("dock", "trim", 0.1, 0.4, 0.25, 17.82, c + 1.0, 0.9)

# a reefer trailer backed onto the open door
with group(25.6, -3.5, 0):
    box("dock", "body", 13.6, 2.5, 2.7, 0, 0, 0.05)
    box("dock", "unit", 0.4, 2.0, 1.4, 6.95, 0, 1.0)                           # trailer reefer unit
    box("dock", "trim", 13.0, 1.0, 0.45, 0.2, 0, -0.45)
    for x in (3.4, 4.7, 6.0):
        for f in (-1, 1): cyl("dock", "tyre", 0.5, 0.32, x - 1.0, f * 1.05, -0.7, "y")
    box("dock", "body", 2.5, 2.5, 3.0, 8.4, 0, -0.65)                         # tractor cab
    box("dock", "glass", 0.05, 2.2, 1.0, 9.66, 0, 1.0)
    for x in (8.1, 9.2):
        for f in (-1, 1): cyl("dock", "tyre", 0.5, 0.34, x, f * 1.05, -0.7, "y")

# ---------------------------------------------------------------- plant room: central rack, chiller, roof condensers
box("plant", "block", 0.25, 5.8, 4.5, 8.0, 7.9, 0)
box("plant", "block", 9.5, 0.25, 1.1, 12.75, 5.0, 0)
for x in (8.0, 12.75, 17.5): box("plant", "block", 0.3, 0.3, 4.5, x, 5.0, 0)
box("plant", "slab", 9.8, 6.0, 0.25, 12.75, 7.9, 4.5)
box("plant", "steel", 4.4, 1.1, 0.16, 12.5, 8.4, 0)                        # rack skid
for x in (10.4, 14.6):
    for y in (7.9, 8.9): box("plant", "steel", 0.08, 0.08, 2.2, x, y, 0.16)
for i in range(4): cyl("plant", "tank", 0.28, 0.8, 11.2 + i * 0.85, 8.4, 0.62)  # compressors
for z in (1.45, 1.75): cyl("plant", "pipe", 0.07, 4.4, 12.5, 8.0, z, "x")
cyl("plant", "tank", 0.34, 2.4, 12.5, 9.75, 0.6, "x")                       # liquid receiver
for x in (11.6, 13.4): box("plant", "steel", 0.1, 0.7, 0.3, x, 9.75, 0)
cyl("plant", "unit", 0.5, 3.4, 16.4, 8.0, 0.85, "y")                       # ammonia chiller shell
for y in (6.9, 9.1): box("plant", "steel", 0.9, 0.12, 0.45, 16.4, y, 0)
box("plant", "panel", 1.2, 0.4, 2.0, 9.0, 10.4, 0)                          # control panel
box("plant", "accent", 1.21, 0.02, 0.06, 9.0, 10.19, 1.8)
for x in (11.0, 12.0):
    cyl("plant", "pipe", 0.07, 2.8, x, 10.4, 3.1)
for i, x in enumerate((10.0, 12.75, 15.5)):                               # air-cooled condensers
    for f in (-1, 1): box("plant", "steel", 0.1, 1.3, 0.5, x + f * 1.0, 7.9, 4.75)
    box("plant", "unit", 2.4, 1.3, 1.0, x, 7.9, 5.25)
    for f in (-0.55, 0.55): cyl("plant", "fan", 0.45, 0.06, x + f, 7.9, 6.28)

# ---------------------------------------------------------------- air handling: AHUs on a platform, ducts, fabric socks
box("ahu", "steel", 13, 2.8, 0.2, -5.5, 9.4, 6.2)
for x in (-11.5, 0.5):
    for y in (8.2, 10.6): box("ahu", "steel", 0.15, 0.15, 6.2, x, y, 0)
for x in (-10.0, -1.5):
    box("ahu", "unit", 4.4, 1.7, 1.7, x, 9.4, 6.4)
    for k in (-1.4, -0.2, 1.0): box("ahu", "trim", 0.05, 1.72, 1.6, x + k, 9.4, 6.45)
    box("ahu", "accent", 4.42, 0.03, 0.08, x, 8.54, 7.7)
cyl("ahu", "duct", 0.36, 17.5, -1.5, -0.2, 8.0, "y")
box("ahu", "duct", 1.0, 0.9, 0.9, -1.5, 8.3, 7.4)
for y in (-6.4, -1.6):
    cyl("ahu", "fabric", 0.42, 32, 0, y, 7.7, "x", seg=24)
    for x in range(-15, 17, 3): box("ahu", "steel", 0.02, 0.02, 0.95, x, y, 8.1)
for x in (-12, -6, 6, 12): cyl("ahu", "duct", 0.22, 1.6, x, -1.6, 7.0)   # drops to the dock area

# ---------------------------------------------------------------- racking and a forklift in the aisle
rack_row("racks", -16.2, 8, -9.05, (0, 1.9, 3.8, 5.7), 7.4, depth=2.2)
rack_row("racks", -16.2, 8, -4.5, (0, 1.9, 3.8, 5.7), 7.4)
for x, y in ((10.5, -8.6), (12.0, -8.6), (10.5, -6.2), (13.6, -1.0), (12.1, -1.0), (10.6, 2.6)):
    box("racks", "pallet", 1.0, 1.2, 0.14, x, y, 0)
    box("racks", random.choice(("stock", "stock2")), 0.96, 1.16, random.uniform(0.9, 1.5), x, y, 0.14)
with group(4.0, -6.5, 0, rz=-90):
    box("racks", "machine", 2.0, 1.1, 0.9, 0, 0, 0.25)
    box("racks", "machine", 0.5, 1.1, 0.6, -0.9, 0, 1.15)                      # counterweight
    for x in (-0.6, 0.6):
        for f in (-1, 1): box("racks", "steel", 0.06, 0.06, 1.1, x, f * 0.5, 1.15)
    box("racks", "steel", 1.3, 1.1, 0.06, 0, 0, 2.25)
    for f in (-1, 1): box("racks", "steel", 0.1, 0.1, 3.0, 1.1, f * 0.35, 0.1)
    for f in (-1, 1): box("racks", "steel", 1.2, 0.12, 0.05, 1.75, f * 0.3, 0.55)
    box("racks", "pallet", 1.0, 1.1, 0.14, 1.75, 0, 0.6)
    box("racks", "stock2", 0.96, 1.06, 1.1, 1.75, 0, 0.74)
    for x in (-0.6, 0.65):
        for f in (-1, 1): cyl("racks", "tyre", 0.27, 0.22, x, f * 0.5, 0.27, "y")

# ---------------------------------------------------------------- the 24/7 service van in the yard
with group(27.5, -16.5, -1.2, rz=28):
    box("van", "body", 4.0, 2.0, 2.0, -0.4, 0, 0.45)
    box("van", "body", 1.3, 2.0, 1.25, 2.25, 0, 0.45)
    box("van", "glass", 0.9, 1.96, 0.75, 2.3, 0, 1.35, rot=(0, -35, 0))
    box("van", "accent", 5.4, 2.03, 0.2, 0.2, 0, 1.05)
    for x in (-1.6, 1.9):
        for f in (-1, 1): cyl("van", "tyre", 0.36, 0.26, x, f * 0.92, 0.36, "y")
    for f in (-1, 1): text("van", "logo", "FTC  24/7", 0.42, -0.6, f * 1.02, 1.4, rot=(90, 0, 0 if f < 0 else 180))

# ---------------------------------------------------------------- objects, one per (part, role)
web = []
for (part, role), bm in GEO.items():
    me = bpy.data.meshes.new(f"{part}.{role}"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(f"{part}.{role}", me); scene.collection.objects.link(ob)
    if part != "shell": ob["part"] = part
    ob["role"] = role
    web.append(ob)

if arg("--glb"):
    for o in scene.objects: o.select_set(o in web)
    bpy.ops.export_scene.gltf(filepath=arg("--glb"), export_format="GLB", use_selection=True, export_extras=True,
                              export_normals=False, export_texcoords=False, export_materials="NONE",
                              export_cameras=False, export_lights=False, export_animations=False, export_yup=True)
    print("GLB ->", arg("--glb"))

# ---------------------------------------------------------------- film: materials, light, camera
PAL = {  # base colour, roughness, metallic
    "floor": ("#B4B8BB", 0.32, 0), "yard": ("#5E6266", 0.9, 0), "slab": ("#9EA2A5", 0.8, 0),
    "clad": ("#D5DADE", 0.45, 0.3), "steel": ("#3B424A", 0.4, 0.6), "roof": ("#3B424A", 0.4, 0.6), "panel": ("#EEF2F4", 0.35, 0),
    "panelfloor": ("#D2D7DA", 0.4, 0), "door": ("#E2E7EA", 0.35, 0.1), "curtain": ("#CFE6F0", 0.1, 0),
    "unit": ("#C5CBD0", 0.4, 0.4), "fan": ("#22272D", 0.6, 0.2), "accent": ("#04AFF0", 0.35, 0),
    "pipe": ("#1D2126", 0.7, 0), "tank": ("#8A949C", 0.3, 0.7), "block": ("#BDB8B0", 0.9, 0),
    "rubber": ("#16191C", 0.9, 0), "plate": ("#6A7178", 0.35, 0.8), "trim": ("#58606A", 0.5, 0.4),
    "upright": ("#2B4A66", 0.45, 0.4), "beam": ("#8E989F", 0.4, 0.5), "pallet": ("#A9875C", 0.8, 0),
    "stock": ("#C7A77B", 0.85, 0), "stock2": ("#E6EBEE", 0.5, 0), "body": ("#F1F3F4", 0.3, 0.2),
    "glass": ("#1B2630", 0.08, 0.2), "tyre": ("#121417", 0.85, 0), "machine": ("#3A3F45", 0.45, 0.3),
    "duct": ("#B6BDC3", 0.35, 0.7), "fabric": ("#DDE3E7", 0.8, 0), "logo": ("#04AFF0", 0.4, 0),
}
CYAN = (0.0151, 0.4287, 0.8714, 1)  # #04AFF0, linear

def srgb(hexs):
    c = [int(hexs[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return [((v + 0.055) / 1.055) ** 2.4 if v > 0.04045 else v / 12.92 for v in c] + [1]

# Steps on the film timeline (frames). Captions on the page use the same split.
STEPS = [("dock", 1, 62), ("cold", 62, 132), ("plant", 132, 182), ("ahu", 182, 232), ("van", 232, 270)]
GLOW = {"dock": 0, "cold": 1, "freezer": 1, "plant": 2, "ahu": 3, "racks": 3, "van": 4}

for ob in web:
    part, role = ob.name.split(".")
    col, rough, metal = PAL.get(role, ("#AAAAAA", 0.5, 0))
    mat = bpy.data.materials.new(ob.name); mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = srgb(col)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if role == "curtain": bsdf.inputs["Alpha"].default_value = 0.7; mat.surface_render_method = "BLENDED"
    if role in ("accent", "logo"):
        bsdf.inputs["Emission Color"].default_value = CYAN; bsdf.inputs["Emission Strength"].default_value = 0.6
    elif part in GLOW and role in ("panel", "door", "unit", "tank", "plate", "duct", "fabric", "body", "machine"):
        # the active step's equipment picks up a faint FTC-cyan glow, then lets it go
        s, a, b = STEPS[GLOW[part]]
        e = bsdf.inputs["Emission Strength"]; bsdf.inputs["Emission Color"].default_value = CYAN
        for f, v in ((a - 8, 0), (a + 6, 0.14), (b - 6, 0.14), (b + 6, 0)):
            e.default_value = v; e.keyframe_insert("default_value", frame=max(1, f))
    ob.data.materials.append(mat)
    bev = ob.modifiers.new("bevel", "BEVEL"); bev.width = 0.012; bev.segments = 1; bev.limit_method = "ANGLE"

# ground to the horizon, with lane marks in the yard
bpy.ops.mesh.primitive_plane_add(size=600, location=(0, 0, -1.21))
g = bpy.context.object; gm = bpy.data.materials.new("ground"); gm.use_nodes = True
gm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = srgb("#7C8084")
gm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.95
g.data.materials.append(gm)
lane = bpy.data.materials.new("lane"); lane.use_nodes = True
lane.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = srgb("#E9ECEE")
for c in (-5.75, -1.25, 3.25, -10.25):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(26, c, -1.195)); o = bpy.context.object
    o.scale = (14, 0.12, 1); o.data.materials.append(lane)

world = bpy.data.worlds.new("sky"); scene.world = world; world.use_nodes = True
bg = world.node_tree.nodes["Background"]; bg.inputs["Color"].default_value = srgb("#C9D6DF"); bg.inputs["Strength"].default_value = 0.9
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); scene.collection.objects.link(sun)
sun.data.energy = 3.2; sun.data.angle = math.radians(3); sun.rotation_euler = (math.radians(50), 0, math.radians(35))
for x in (-10, 1.5):   # cool fill inside the cold rooms
    l = bpy.data.objects.new("cold", bpy.data.lights.new("cold", "AREA")); scene.collection.objects.link(l)
    l.data.energy = 900; l.data.size = 6; l.data.color = (0.85, 0.93, 1.0); l.location = (x, 5.5, 7.5)

cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scene.collection.objects.link(cam); scene.camera = cam
cam.data.lens = 26; cam.data.clip_start = 0.1; cam.data.clip_end = 900
tgt = bpy.data.objects.new("target", None); scene.collection.objects.link(tgt)
tc = cam.constraints.new("TRACK_TO"); tc.target = tgt; tc.track_axis = "TRACK_NEGATIVE_Z"; tc.up_axis = "UP_Y"

# (frame, camera, look-at). Exterior -> through the open dock door -> cold room -> over the freezer ->
# plant room -> roof condensers -> crane up over the building -> down to the service van -> pull back.
PATH = [
    (1,   (46, -40, 21),   (6, -2, 1)),
    (34,  (34, -13, 2.6),  (18, -3.5, 1.2)),
    (62,  (14, -3.5, 2.1), (2, 0, 1.6)),
    (84,  (-10, -4, 2.1),  (-10, 6, 2.0)),
    (106, (-9.5, 1.9, 3.7), (-11.5, 10, 4.4)),
    (132, (-3.5, 0, 8.8),  (1.5, 6, 0.5)),
    (156, (10.6, 2.4, 3.1), (12.6, 9.5, 0.9)),
    (182, (12.5, 0.5, 11.8), (13, 8, 5.3)),
    (212, (2, -30, 24),     (-2, 2, 4)),
    (232, (-14, -24, 15),   (-4, 0, 6)),
    (252, (34, -27, 2.2),   (27.5, -16.5, -0.2)),
    (270, (58, -50, 22),    (12, -6, 0)),
]
for f, p, t in PATH:
    cam.location = p; cam.keyframe_insert("location", frame=f)
    tgt.location = t; tgt.keyframe_insert("location", frame=f)

scene.frame_start, scene.frame_end = 1, 270
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x, scene.render.resolution_y = int(arg("--w", 1280)), int(arg("--h", 720))
scene.render.image_settings.file_format = "JPEG"; scene.render.image_settings.quality = 92
ee = scene.eevee
for k, v in (("taa_render_samples", int(arg("--samples", 48))), ("use_raytracing", True), ("use_shadows", True)):
    if hasattr(ee, k): setattr(ee, k, v)
try: scene.view_settings.look = "AgX - Medium High Contrast"
except Exception: pass

if arg("--blend"): bpy.ops.wm.save_as_mainfile(filepath=arg("--blend"))

def render_frames(frames, out):
    for f in frames:
        scene.frame_set(f); scene.render.filepath = f"{out}/f{f:04d}.jpg"
        bpy.ops.render.render(write_still=True)

if arg("--preview"):
    ee.taa_render_samples = 12
    render_frames([int(x) for x in arg("--frames", ",".join(str(p[0]) for p in PATH)).split(",")], arg("--preview"))
if arg("--render"):
    # --step 2 renders every other frame (what the site scrubs) plus the five step posters
    KEYS = (34, 106, 156, 212, 252)
    fr = set(range(int(arg("--from", 1)), int(arg("--to", 270)) + 1, int(arg("--step", 1)))) | set(KEYS)
    render_frames(sorted(fr), arg("--render"))
