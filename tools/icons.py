"""Isometric duotone icons for the scope-of-work grid and the services, generated from simple 3D primitives.

Each icon is built in 3D (X right-back, Y left-back, Z up), projected to a 30-degree isometric view and
auto-fitted to a 64x64 viewBox. Faces carry tone classes (t = top, l = left, r = right, a = solid accent,
k = line detail) so CSS colours them from the theme accent; parts with class "mv" animate on hover.
"""
import math

C = math.cos(math.pi / 6)


def P(x, y, z):
    return ((x - y) * C, (x + y) * 0.5 - z)


class Icon:
    def __init__(self):
        self.ops = []  # (kind, cls, pts2d or extra)

    def poly(self, pts, cls):
        self.ops.append(("poly", cls, [P(*p) for p in pts]))

    def line(self, pts, cls="k"):
        self.ops.append(("line", cls, [P(*p) for p in pts]))

    def group(self, cls):
        self.ops.append(("g", cls, None))

    def end(self):
        self.ops.append(("/g", None, None))

    def box(self, x, y, z, w, d, h, tone=""):
        """Axis-aligned box; draws the three visible faces (top, +X face, +Y face)."""
        X, Y, Z = x + w, y + d, z + h
        self.poly([(x, Y, z), (X, Y, z), (X, Y, Z), (x, Y, Z)], "l " + tone)   # +Y face (front-left)
        self.poly([(X, y, z), (X, Y, z), (X, Y, Z), (X, y, Z)], "r " + tone)   # +X face (front-right)
        self.poly([(x, y, Z), (X, y, Z), (X, Y, Z), (x, Y, Z)], "t " + tone)   # top

    def ring(self, centre, axis, r, n=28):
        cx, cy, cz = centre
        out = []
        for i in range(n):
            a = 2 * math.pi * i / n
            u, v = r * math.cos(a), r * math.sin(a)
            out.append({"x": (cx, cy + u, cz + v), "y": (cx + u, cy, cz + v), "z": (cx + u, cy + v, cz)}[axis])
        return out

    def cyl(self, base, axis, r, length, tone="", cap=True):
        """Cylinder along an axis from base; side is the hull of both end rings, the far-visible end cap on top."""
        bx, by, bz = base
        end = {"x": (bx + length, by, bz), "y": (bx, by + length, bz), "z": (bx, by, bz + length)}[axis]
        a, b = self.ring(base, axis, r), self.ring(end, axis, r)
        hull = convex_hull([P(*p) for p in a + b])
        self.ops.append(("poly", ("l " if axis != "x" else "r ") + tone, hull))
        if cap:
            self.ops.append(("poly", "t " + tone, [P(*p) for p in b]))

    def disc(self, centre, axis, r, cls):
        self.ops.append(("poly", cls, [P(*p) for p in self.ring(centre, axis, r)]))

    def svg(self):
        pts = [p for k, _, ps in self.ops if ps for p in ps]
        x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
        y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
        s = 52 / max(x1 - x0, y1 - y0)
        ox, oy = 32 - (x0 + x1) / 2 * s, 32 - (y0 + y1) / 2 * s
        f = lambda p: f"{p[0] * s + ox:.1f},{p[1] * s + oy:.1f}"
        out = []
        for kind, cls, ps in self.ops:
            if kind == "g":
                out.append(f'<g class="{cls}">')
            elif kind == "/g":
                out.append("</g>")
            elif kind == "poly":
                out.append(f'<polygon class="{cls.strip()}" points="{" ".join(map(f, ps))}"/>')
            else:
                out.append(f'<polyline class="{cls}" points="{" ".join(map(f, ps))}"/>')
        # shadow ellipse under the object
        sy = y1 * s + oy
        return f'<ellipse class="sh" cx="32" cy="{min(sy + 1, 62):.1f}" rx="20" ry="3"/>' + "".join(out)


def convex_hull(points):
    pts = sorted(set((round(x, 3), round(y, 3)) for x, y in points))
    if len(pts) < 3:
        return pts
    def cross(o, a, b): return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0: hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def face_x(X, y0, z0, pts):
    """Map 2D (a, b) points onto the +X face plane: a along Y, b along Z."""
    return [(X, y0 + a, z0 + b) for a, b in pts]


def face_y(Y, x0, z0, pts):
    return [(x0 + a, Y, z0 + b) for a, b in pts]


def build():
    I = {}

    # Commercial refrigeration: an upright glass-door display cabinet
    i = Icon(); i.box(0, 0, 0, 14, 12, 26)
    i.poly(face_x(14, 2, 3, [(0, 0), (8, 0), (8, 18), (0, 18)]), "a2")
    for zz in (8, 13, 18): i.line(face_x(14.01, 2, 0, [(0, zz), (8, zz)]))
    i.line(face_x(14.02, 9, 9, [(0, 0), (0, 5)]), "k2")
    i.box(0, 0, 26, 14, 12, 3, "dk"); i.line(face_y(12.01, 2, 27.5, [(0, 0), (10, 0)]), "k2")
    I["commercial-refrigeration"] = i.svg()

    # Industrial refrigeration: a compressor rack on a skid
    i = Icon(); i.box(0, 0, 0, 26, 12, 3, "dk")
    for yy in (1.5, 7.5): i.cyl((3, yy + 1.5, 6), "x", 2.6, 16, "", True)
    i.box(20, 1, 3, 4, 10, 12); i.line([(22, 2, 15), (22, 2, 19), (8, 2, 19), (8, 2, 9)], "k2")
    I["industrial-refrigeration"] = i.svg()

    # Ammonia cooling: a horizontal receiver vessel on saddles, with an accent band
    i = Icon(); i.box(4, 2, 0, 3, 10, 4, "dk"); i.box(19, 2, 0, 3, 10, 4, "dk")
    i.cyl((0, 7, 9), "x", 6, 26)
    i.line([(9, 7 + 6 * math.cos(a), 9 + 6 * math.sin(a)) for a in [k * math.pi / 14 for k in range(-7, 15)]], "k2")
    i.line([(17, 7 + 6 * math.cos(a), 9 + 6 * math.sin(a)) for a in [k * math.pi / 14 for k in range(-7, 15)]], "k2")
    i.cyl((12, 5, 15), "z", 1.4, 6, "a2")
    I["ammonia-cooling"] = i.svg()

    # Cold room: an insulated panel room with a door and a monobloc on the roof
    i = Icon(); i.box(0, 0, 0, 22, 18, 16)
    i.poly(face_x(22, 9, 0, [(0, 0), (6, 0), (6, 12), (0, 12)]), "a2")
    i.line(face_x(22.02, 9, 0, [(1, 6), (2.2, 6)]), "k2")
    for k in (6, 12): i.line(face_y(18.01, 0, 0, [(k, 0), (k, 16)]))
    i.group("mv flo"); i.box(4, 3, 16, 9, 7, 4, "dk"); i.disc((13.01, 6.5, 18), "x", 1.6, "a3"); i.end()
    I["cold-rooms"] = i.svg()

    # Air conditioning: a wall split unit with cool air flowing out
    i = Icon(); i.box(0, 0, 10, 26, 6, 8)
    i.line(face_y(6.01, 2, 11.5, [(0, 0), (22, 0)]), "k2")
    i.group("mv air")
    for k in range(4):
        x = 4 + k * 6
        i.line([(x, 8, 8), (x + 1, 10, 5), (x, 12, 2), (x + 1, 14, -1)], "k3")
    i.end()
    I["air-conditioning"] = i.svg()

    # Exhaust & ventilation: a roof fan housing with a spinning impeller
    i = Icon(); i.box(0, 0, 0, 20, 20, 6, "dk"); i.cyl((10, 10, 6), "z", 9, 6)
    i.group("mv spin")
    for k in range(5):
        a = 2 * math.pi * k / 5
        i.poly([(10, 10, 12.1), (10 + 8 * math.cos(a), 10 + 8 * math.sin(a), 12.1), (10 + 7 * math.cos(a + .6), 10 + 7 * math.sin(a + .6), 12.1)], "a2")
    i.disc((10, 10, 12.2), "z", 1.8, "a3")
    i.end()
    I["exhaust-ventilation"] = i.svg()

    # Air handling: a fabric sock duct on hangers, air dotted out along it
    i = Icon(); i.box(0, 4, 0, 5, 10, 14, "dk")
    i.cyl((5, 9, 9), "x", 4.5, 26)
    for x in (12, 24): i.line([(x, 9, 13.5), (x, 9, 20)], "k")
    i.group("mv air")
    for x in (10, 16, 22, 28): i.line([(x, 9, 3.5), (x, 9, 1)], "k3")
    i.end()
    I["air-handling"] = i.svg()

    # Thermal & acoustic insulation: a pipe with an insulation sleeve, cut back to show the layers
    i = Icon(); i.cyl((0, 6, 6), "x", 2, 32, "dk")
    i.cyl((7, 6, 6), "x", 5.5, 16, "", False); i.disc((23, 6, 6), "x", 5.5, "t"); i.disc((23.01, 6, 6), "x", 3.6, "a2"); i.disc((23.02, 6, 6), "x", 2, "dk t")
    for x in (11, 15, 19): i.line([(x, 6 + 5.5 * math.cos(a), 6 + 5.5 * math.sin(a)) for a in [k * math.pi / 12 for k in range(-6, 13)]], "k")
    I["insulation"] = i.svg()

    # Fire-rated materials: a fire board standing between the flame and the room it protects
    i = Icon()
    i.box(0, 0, 0, 3, 20, 22)
    i.poly(face_x(3.01, 1.5, 1.5, [(0, 0), (17, 0), (17, 19), (0, 19)]), "a1")
    i.group("mv fl")
    fl = [(9, 0), (16, 8), (15, 17), (12.5, 13), (10, 25), (6, 14), (3.5, 18), (2.5, 8)]
    core = [(9, 0), (12.5, 5), (12, 11), (10, 8.5), (8.5, 13), (6.5, 7), (6, 4)]
    i.poly([(4 + a, 20, b) for a, b in fl], "a2"); i.poly([(4 + a, 20.2, b) for a, b in core], "a3")
    i.end()
    I["fire-rated-materials"] = i.svg()

    # Insulated panels: three sandwich panels, staggered, the insulating core showing on the top edge
    i = Icon()
    for k in range(3):
        x, h = k * 6, 22 - k * 3
        i.box(x, 0, 0, 3, 18, h)
        i.poly([(x + 0.6, 0.6, h + 0.01), (x + 2.4, 0.6, h + 0.01), (x + 2.4, 17.4, h + 0.01), (x + 0.6, 17.4, h + 0.01)], "a3")
    I["insulated-panels"] = i.svg()

    # Hygiene systems: a clean wall panel with a polished floor and sparkles
    i = Icon(); i.box(0, 0, 0, 24, 18, 1.5, "dk"); i.box(0, 0, 1.5, 3, 18, 20)
    for k in (6, 12): i.line(face_x(3.01, 0, 1.5, [(k, 0), (k, 20)]))
    i.group("mv tw")
    for (cx, cz, r) in ((10, 14, 3.2), (15, 8, 2)):
        i.poly(face_x(3.05, 0, 0, [(cx, cz + r), (cx + r * .28, cz + r * .28), (cx + r, cz), (cx + r * .28, cz - r * .28), (cx, cz - r), (cx - r * .28, cz - r * .28), (cx - r, cz), (cx - r * .28, cz + r * .28)]), "a3")
    i.end()
    I["hygiene-systems"] = i.svg()

    # Geocellular tanks: stacked lattice crates
    i = Icon()
    for (x, y, z) in ((0, 0, 0), (10, 0, 0), (0, 10, 0), (10, 10, 0), (0, 0, 8), (10, 0, 8)):
        i.box(x, y, z, 10, 10, 8)
        if x == 10: i.line(face_x(20.01, y, z, [(2, 2), (8, 6)])); i.line(face_x(20.01, y, z, [(2, 6), (8, 2)]))
        if y == 10: i.line(face_y(20.01, x, z, [(2, 2), (8, 6)])); i.line(face_y(20.01, x, z, [(2, 6), (8, 2)]))
    i.poly(face_y(10.02, 0, 8, [(1, 1), (19, 1), (19, 7), (1, 7)]), "a1")
    I["geocellular-tanks"] = i.svg()

    # Storage & racking: a pallet rack with loads on two levels
    i = Icon()
    for (x, y) in ((0, 0), (24, 0), (0, 8), (24, 8)): i.box(x, y, 0, 1.6, 1.6, 26, "dk")
    for z in (8, 18):
        i.box(0, 0, z, 25.6, 1.2, 1.2, "dk"); i.box(0, 8.4, z, 25.6, 1.2, 1.2, "dk")
    i.box(2.5, 1.5, 9.2, 9, 7, 7, "acc"); i.box(13.5, 1.5, 9.2, 9, 7, 5); i.box(2.5, 1.5, 19.2, 9, 7, 5); i.box(13.5, 1.5, 19.2, 9, 7, 6.5, "acc")
    I["storage-racking"] = i.svg()

    # Industrial doors: a dock wall with a sectional door sliding up
    i = Icon(); i.box(0, 0, 0, 4, 26, 22)
    i.poly(face_x(4, 5, 0, [(0, 0), (16, 0), (16, 16), (0, 16)]), "dk r")
    i.group("mv up")
    i.poly(face_x(4.05, 5, 5, [(0, 0), (16, 0), (16, 11), (0, 11)]), "a2")
    for k in (2.8, 5.6, 8.4): i.line(face_x(4.1, 5, 5, [(0, k), (16, k)]), "k2")
    i.end()
    i.box(4, 4, 0, 6, 18, 1.2, "dk")
    I["industrial-doors"] = i.svg()

    # Material handling: a forklift whose forks lift on hover
    i = Icon(); i.box(0, 0, 3, 14, 10, 7)
    i.box(2, 1, 10, 8, 8, 1, "dk")
    for (x, y) in ((2, 1), (9, 1), (2, 9), (9, 9)): pass
    i.line([(2, 1, 11), (2, 1, 19), (10, 1, 19), (10, 1, 11)], "k2"); i.line([(2, 9, 11), (2, 9, 19), (10, 9, 19), (10, 9, 11)], "k2")
    i.box(14, 1, 0, 1.4, 8, 22, "dk")
    i.group("mv lift"); i.box(15.4, 2, 1, 9, 1.4, 1, "acc"); i.box(15.4, 6.6, 1, 9, 1.4, 1, "acc"); i.box(17, 1.5, 2, 6, 7, 5, ""); i.end()
    i.disc((3.5, 10.01, 3), "y", 3, "dk l"); i.disc((11.5, 10.01, 3), "y", 3, "dk l")
    I["material-handling"] = i.svg()

    # Spare parts: an open parts bin with a gear and a wrench
    i = Icon(); i.box(0, 0, 0, 20, 14, 9)
    i.poly([(1.5, 1.5, 9.01), (18.5, 1.5, 9.01), (18.5, 12.5, 9.01), (1.5, 12.5, 9.01)], "dk t")
    i.group("mv spin2")
    teeth = []
    for k in range(16):
        a = 2 * math.pi * k / 16; r = 6 if k % 2 == 0 else 4.6
        teeth.append((10 + r * math.cos(a), 7 + r * math.sin(a), 9.3))
    i.poly(teeth, "a2"); i.disc((10, 7, 9.4), "z", 1.8, "dk t")
    i.end()
    i.poly(face_y(14.02, 3, 1, [(0, 0), (2, 0), (12, 11), (14, 11), (15, 13), (13, 15), (11, 14), (11, 12)]), "a3")
    I["spare-parts"] = i.svg()

    # Valves & copper: a copper pipe run with a valve body and a handwheel
    i = Icon(); i.cyl((0, 6, 5), "x", 2.4, 30, "dk")
    i.box(11, 2.5, 1.5, 8, 7, 7)
    i.box(14, 5, 8.5, 2, 2, 5, "dk")
    i.group("mv spin3"); i.disc((15, 6, 13.6), "z", 5.5, "a2"); i.disc((15, 6, 13.7), "z", 3.6, "t"); i.disc((15, 6, 13.8), "z", 1.2, "a3"); i.end()
    I["valves-copper"] = i.svg()

    # Services ---------------------------------------------------------------
    # Engineering: a drawing sheet with a plan on it and a pencil
    i = Icon(); i.box(0, 0, 0, 26, 18, 1.5)
    i.poly([(3, 3, 1.51), (23, 3, 1.51), (23, 15, 1.51), (3, 15, 1.51)], "a1")
    for (a, b) in (((5, 5), (14, 5)), ((14, 5), (14, 12)), ((5, 12), (21, 12)), ((18, 5), (21, 5)), ((5, 5), (5, 12))):
        i.line([(a[0], a[1], 1.6), (b[0], b[1], 1.6)], "k2")
    i.group("mv flo"); i.cyl((12, 20, 4), "x", 1.2, 14, "acc"); i.end()
    I["engineering"] = i.svg()

    # Contracting: a building going up, with a crane
    i = Icon(); i.box(0, 0, 0, 12, 12, 10); i.box(0, 0, 10, 12, 12, 8, "acc")
    for k in (4, 8): i.line(face_x(12.01, 0, 0, [(k, 0), (k, 18)]))
    i.box(16, 2, 0, 1.6, 1.6, 30, "dk")
    i.line([(17, 3, 30), (-4, 3, 30)], "k2"); i.line([(17, 3, 30), (24, 3, 30)], "k2")
    i.group("mv flo"); i.line([(2, 3, 30), (2, 3, 22)], "k3"); i.box(0.5, 1.5, 19.5, 3, 3, 2.5, "acc"); i.end()
    I["contracting"] = i.svg()

    # Maintenance: a condensing unit with a wrench turning on it
    i = Icon(); i.box(0, 0, 0, 22, 12, 14)
    i.disc((22.01, 6, 7), "x", 4.8, "dk r")
    i.group("mv spin4")
    for k in range(4):
        a = 2 * math.pi * k / 4
        i.poly([(22.05, 6, 7), (22.05, 6 + 4.2 * math.cos(a), 7 + 4.2 * math.sin(a)), (22.05, 6 + 3.6 * math.cos(a + .7), 7 + 3.6 * math.sin(a + .7))], "a2")
    i.end()
    i.poly(face_y(12.05, 2, 2, [(0, 1), (2, 0), (11, 8), (13, 7), (15, 9), (14, 12), (12, 11), (11, 10)]), "a3")
    I["maintenance"] = i.svg()

    # Supply chain: a truck with cargo
    i = Icon(); i.box(0, 0, 3, 18, 10, 12); i.box(18, 0.5, 3, 7, 9, 8, "acc")
    i.poly(face_x(25.01, 1.5, 7, [(0, 0), (7, 0), (7, 3.5), (0, 3.5)]), "dk r")
    for (x, y) in ((4, 10.01), (14, 10.01), (21, 9.51)): i.disc((x, y, 3), "y", 2.8, "dk l")
    i.group("mv flo"); i.box(3, 2, 15, 5, 5, 4, "acc"); i.box(9, 3, 15, 4, 4, 3); i.end()
    I["supply-chain"] = i.svg()
    return I


ICONS = build()
