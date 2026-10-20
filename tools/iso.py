"""Mini-3D-Renderer (Parallelprojektion + Maleralgorithmus) fuer die Anleitungsbilder.

Die Flaechen koennen das echte 2D-Dekor der Vorlagen tragen, weil eine
Parallelprojektion eine affine Abbildung ist.
"""
import math
from zug import mix, f, pts_str

INNER = '#F1ECE3'


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def mul(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def norm(a):
    l = math.sqrt(dot(a, a)) or 1
    return (a[0] / l, a[1] / l, a[2] / l)


def length(a):
    return math.sqrt(dot(a, a))


def rot_about(p, origin, axis, ang):
    """Punkt p um Achse (origin, axis) um ang Grad drehen (Rodrigues)."""
    k = norm(axis)
    v = sub(p, origin)
    a = math.radians(ang)
    c, s = math.cos(a), math.sin(a)
    r = add(add(mul(v, c), mul(cross(k, v), s)), mul(k, dot(k, v) * (1 - c)))
    return add(origin, r)


class Face:
    def __init__(self, pts, col, normal=None, frame=None, decor=None, back=None, edge=None, outline=True):
        self.pts = pts
        self.col = col
        self.back = back
        self.frame = frame
        self.decor = decor
        self.edge = edge
        self.outline = outline
        if normal is None:
            if frame is not None:
                normal = cross(frame[2], frame[1])
            else:
                n = (0.0, 0.0, 0.0)
                for i in range(len(pts)):
                    a, b = pts[i], pts[(i + 1) % len(pts)]
                    n = add(n, ((a[1] - b[1]) * (a[2] + b[2]), (a[2] - b[2]) * (a[0] + b[0]), (a[0] - b[0]) * (a[1] + b[1])))
                normal = mul(n, -1)
        self.n = norm(normal)

    def center(self):
        k = len(self.pts)
        return (sum(p[0] for p in self.pts) / k, sum(p[1] for p in self.pts) / k, sum(p[2] for p in self.pts) / k)


def quad(P0, U, V, col, decor=None, back=None, **kw):
    """Viereck mit Ecke P0 (links oben der bedruckten Seite), U nach rechts, V nach unten.
    Die bedruckte Seite zeigt in Richtung V x U."""
    pts = [P0, add(P0, U), add(add(P0, U), V), add(P0, V)]
    return Face(pts, col, frame=(P0, U, V), decor=decor, back=back, **kw)


def transform_face(fc, fn):
    pts = [fn(p) for p in fc.pts]
    frame = None
    if fc.frame:
        P0, U, V = fc.frame
        q0 = fn(P0)
        frame = (q0, sub(fn(add(P0, U)), q0), sub(fn(add(P0, V)), q0))
    nf = Face(pts, fc.col, normal=sub(fn(add(fc.pts[0], fc.n)), fn(fc.pts[0])), frame=frame,
              decor=fc.decor, back=fc.back, edge=fc.edge, outline=fc.outline)
    return nf


def move(faces, d):
    return [transform_face(fc, lambda p: add(p, d)) for fc in faces]


def rotate(faces, origin, axis, ang):
    return [transform_face(fc, lambda p: rot_about(p, origin, axis, ang)) for fc in faces]


def cuboid(x0, y0, z0, lx, ly, lz, col, decor=None, skip=(), back=None, cols=None):
    """Quader. decor/cols: dict mit front/back/left/right/top/bottom."""
    x1, y1, z1 = x0 + lx, y0 + ly, z0 + lz
    decor = decor or {}
    cols = cols or {}
    F = {
        'front': quad((x0, y0, z1), (lx, 0, 0), (0, 0, -lz), cols.get('front', col), decor.get('front'), back),
        'back': quad((x1, y1, z1), (-lx, 0, 0), (0, 0, -lz), cols.get('back', col), decor.get('back'), back),
        'left': quad((x0, y1, z1), (0, -ly, 0), (0, 0, -lz), cols.get('left', col), decor.get('left'), back),
        'right': quad((x1, y0, z1), (0, ly, 0), (0, 0, -lz), cols.get('right', col), decor.get('right'), back),
        'top': quad((x0, y1, z1), (lx, 0, 0), (0, -ly, 0), cols.get('top', col), decor.get('top'), back),
        'bottom': quad((x0, y0, z0), (lx, 0, 0), (0, ly, 0), cols.get('bottom', col), decor.get('bottom'), back),
    }
    return [F[k] for k in ('front', 'back', 'left', 'right', 'top', 'bottom') if k not in skip]


def cyl_x(x0, x1, cy, cz, r, col, n=40, bands=(), cap0=None, cap_decor=None):
    """Zylinder entlang x. bands: Liste (xa, xb, farbe). cap0: Farbe Stirnflaeche bei x0."""
    cuts = sorted(set([x0, x1] + [b[0] for b in bands] + [b[1] for b in bands]))
    faces = []
    for xa, xb in zip(cuts, cuts[1:]):
        c = col
        for b in bands:
            if b[0] <= xa and xb <= b[1]:
                c = b[2]
        for i in range(n):
            a0 = 2 * math.pi * i / n
            a1 = 2 * math.pi * (i + 1) / n
            p = lambda x, a: (x, cy + r * math.cos(a), cz + r * math.sin(a))
            pts = [p(xa, a0), p(xb, a0), p(xb, a1), p(xa, a1)]
            am = (a0 + a1) / 2
            faces.append(Face(pts, c, normal=(0, math.cos(am), math.sin(am)), outline=False))
    if cap0:
        pts = [(x0, cy + r * math.cos(2 * math.pi * i / n), cz + r * math.sin(2 * math.pi * i / n)) for i in range(n)]
        frame = ((x0, cy + r, cz + r), (0, -2 * r, 0), (0, 0, -2 * r)) if cap_decor else None
        faces.append(Face(pts, cap0, normal=(-1, 0, 0), frame=frame, decor=cap_decor))
    return faces


def cyl_z(cx, cy, z0, z1, r, col, n=32, top_col=None, bands=()):
    faces = []
    cuts = sorted(set([z0, z1] + [b[0] for b in bands] + [b[1] for b in bands]))
    for za, zb in zip(cuts, cuts[1:]):
        c = col
        for b in bands:
            if b[0] <= za and zb <= b[1]:
                c = b[2]
        for i in range(n):
            a0 = 2 * math.pi * i / n
            a1 = 2 * math.pi * (i + 1) / n
            p = lambda z, a: (cx + r * math.cos(a), cy + r * math.sin(a), z)
            am = (a0 + a1) / 2
            faces.append(Face([p(zb, a0), p(zb, a1), p(za, a1), p(za, a0)], c,
                              normal=(math.cos(am), math.sin(am), 0), outline=False))
    if top_col:
        pts = [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n), z1) for i in range(n)]
        faces.append(Face(pts, top_col, normal=(0, 0, 1)))
    return faces


def disc_y(cx, y, cz, r, col, decor=None, facing=-1, n=36):
    pts = [(cx + r * math.cos(2 * math.pi * i / n), y, cz + r * math.sin(2 * math.pi * i / n)) for i in range(n)]
    if facing < 0:
        frame = ((cx - r, y, cz + r), (2 * r, 0, 0), (0, 0, -2 * r))
    else:
        frame = ((cx + r, y, cz + r), (-2 * r, 0, 0), (0, 0, -2 * r))
    return Face(pts, col, normal=(0, facing, 0), frame=frame, decor=decor)


def flat_y(pts2, y, col, decor=None, facing=-1, box=None):
    """Flaches Teil (z.B. Rauchwolke) in der Ebene y; pts2 = [(x,z)]."""
    pts = [(x, y, z) for x, z in pts2]
    frame = None
    if box:
        x0, z1, w, h = box
        frame = ((x0, y, z1), (w, 0, 0), (0, 0, -h))
    return Face(pts, col, normal=(0, facing, 0), frame=frame, decor=decor)


class Cam:
    def __init__(self, yaw=25, pitch=24):
        y, p = math.radians(yaw), math.radians(pitch)
        self.d = (math.sin(y) * math.cos(p), math.cos(y) * math.cos(p), -math.sin(p))
        self.r = (math.cos(y), -math.sin(y), 0.0)
        self.u = cross(self.r, self.d)
        self.L = norm((-0.45, -0.75, 1.0))

    def p(self, P):
        return (dot(P, self.r), -dot(P, self.u))

    def depth(self, P):
        return dot(P, self.d)


_uid = [0]


def render(groups, cam=None, pad=6, arrows=(), lw=None, sort=True, label=None):
    """groups: Liste von Flaechenlisten, in dieser Reihenfolge gezeichnet (innerhalb nach Tiefe)."""
    cam = cam or Cam()
    allp = [cam.p(p) for g in groups for fc in g for p in fc.pts]
    for a, b in arrows:
        allp += [cam.p(a), cam.p(b)]
    xs = [p[0] for p in allp]
    ys = [p[1] for p in allp]
    x0, x1, y0, y1 = min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad
    W, H = x1 - x0, y1 - y0
    lw = lw or max(W, H) / 380.0
    o = []
    for g in groups:
        items = sorted(g, key=lambda fc: -cam.depth(fc.center())) if sort else g
        for fc in items:
            o.append(draw_face(fc, cam, lw))
    for a, b in arrows:
        o.append(arrow(cam.p(a), cam.p(b), lw))
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s %s %s %s" preserveAspectRatio="xMidYMid meet">%s</svg>' % (
        f(x0), f(y0), f(W), f(H), ''.join(o))


def draw_face(fc, cam, lw):
    pts = [cam.p(p) for p in fc.pts]
    facing = dot(fc.n, cam.d) < 0
    n = fc.n if facing else mul(fc.n, -1)
    col = fc.col if facing else (fc.back or INNER)
    b = 0.80 + 0.20 * max(0.0, dot(n, cam.L))
    ps = pts_str(pts)
    o = ['<polygon points="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (ps, col, col, f(lw * 0.6))]
    if facing and fc.decor and fc.frame:
        P0, U, V = fc.frame
        w, h = length(U), length(V)
        s0 = cam.p(P0)
        su = cam.p(add(P0, U))
        sv = cam.p(add(P0, V))
        a, bb = (su[0] - s0[0]) / w, (su[1] - s0[1]) / w
        c, d = (sv[0] - s0[0]) / h, (sv[1] - s0[1]) / h
        _uid[0] += 1
        cid = 'k%d' % _uid[0]
        o.append('<clipPath id="%s"><polygon points="%s"/></clipPath><g clip-path="url(#%s)"><g transform="matrix(%s,%s,%s,%s,%s,%s)">%s</g></g>' % (
            cid, ps, cid, f(a), f(bb), f(c), f(d), f(s0[0]), f(s0[1]), fc.decor(w, h)))
    if b < 0.999:
        o.append('<polygon points="%s" fill="#000000" opacity="%.3f"/>' % (ps, 1 - b))
    if fc.outline:
        o.append('<polygon points="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
            ps, fc.edge or mix(col, '#000000', 0.38), f(lw)))
    return ''.join(o)


def arrow(a, b, lw, col='#C0675A'):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    ux, uy = dx / L, dy / L
    hs = lw * 9
    p1 = (b[0] - ux * hs - uy * hs * 0.6, b[1] - uy * hs + ux * hs * 0.6)
    p2 = (b[0] - ux * hs + uy * hs * 0.6, b[1] - uy * hs - ux * hs * 0.6)
    return ('<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="%s" stroke-linecap="round" stroke-dasharray="%s,%s"/>'
            '<polygon points="%s" fill="%s"/>' % (
                f(a[0]), f(a[1]), f(b[0] - ux * hs * 0.8), f(b[1] - uy * hs * 0.8), col, f(lw * 2.2), f(lw * 5), f(lw * 3),
                pts_str([b, p1, p2]), col))
