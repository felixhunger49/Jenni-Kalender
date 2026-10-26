"""3D-Modelle von Kaestchen, Waggon und Lok fuer die Anleitungsbilder (Masse wie Vorlagen)."""
from iso import *
from zug import (WAGONS, LOCO, WOOD, WOOD2, WOODD, TAB, CREAM, CREAM2, BOILER_R, CHIM_R, CAB_A, CAB_B, CAB_H,
                 CAB_ROOF, CH_L, CH_W, CH_H, WG_L, WG_W, WG_H, WG_WHEEL_R, WG_WHEELS, LOCO_REAR_R, LOCO_FRONT_R,
                 BOX_W, BOX_D, BOX_H,
                 wagon_side, wagon_endwall, box_wall, lid_top, wheel_decor,
                 chassis_side, chassis_front, chassis_back, chassis_top, cab_side, cab_front, cab_back, cab_roof,
                 boiler_disc, cloud_shape, cloud_decor, mix, chimney_profile)

Z0 = 8.0          # Bodenhoehe ueber dem Tisch (Raeder ragen 8 mm unter)
WG = WG_L
T = 0.6           # Kartondicke-Zuschlag fuer die Aussenmasse der Kaestchen


# ---------------------------------------------------------------- Kaestchen
def base_col(W):
    return box_wall(W)[1]


def _bdec(W):
    deco, base = box_wall(W)
    return dict(front=deco, back=deco, left=deco, right=deco), base


def box_bottom(W, x, y, z, lx=BOX_W, ly=BOX_D, lz=BOX_H):
    d, base = _bdec(W)
    return cuboid(x, y, z, lx, ly, lz, base, d, skip=('top',))


def box_closed(W, num, x, y, z, lx=BOX_W, ly=BOX_D):
    d, base = _bdec(W)
    d['top'] = lid_top(W, num)
    return [cuboid(x, y, z, lx, ly, BOX_H, base, d, cols=dict(top=mix(W['c'], '#FFFFFF', 0.25)))]


def box_lid_open(W, num, ang=105, tuck=True, lx=BOX_W, ly=BOX_D, lz=BOX_H):
    """Kaestchen mit aufgeklapptem Deckel (Scharnier an der Rueckwand)."""
    lidc = mix(W['c'], '#FFFFFF', 0.25)
    walls = box_bottom(W, 0, 0, 0, lx, ly, lz)
    top = quad((0, ly, lz), (lx, 0, 0), (0, -ly, 0), lidc, lid_top(W, num), back=lidc)
    parts = [top]
    if tuck:
        parts.append(quad((0, 0, lz), (lx, 0, 0), (0, 0, -13), lidc, back=lidc))
    parts = rotate(parts, (0, ly, lz), (1, 0, 0), -ang)
    dust = []
    for x, nx in ((0, -1), (lx, 1)):
        dust.append(Face([(x, ly, lz), (x, 0, lz), (x, 3, lz + 11), (x, ly - 3, lz + 11)],
                         base_col(W), normal=(nx, 0, 0), back=base_col(W)))
    return [walls + dust, parts]


def box_folding(W):
    """Waende stehen als Ring, Boden klappt noch auf."""
    d, base = _bdec(W)
    lx, ly = BOX_W, BOX_D
    walls = cuboid(0, 0, 0, lx, ly, 38, base, d, skip=('top', 'bottom'))
    t = 7
    tabs = [Face([(0, 0, 0), (lx, 0, 0), (lx - 2, t, 0), (2, t, 0)], TAB, normal=(0, 0, 1), back=TAB),
            Face([(0, ly, 0), (0, 0, 0), (t, 2, 0), (t, ly - 2, 0)], TAB, normal=(0, 0, 1), back=TAB),
            Face([(lx, ly, 0), (0, ly, 0), (2, ly - t, 0), (lx - 2, ly - t, 0)], TAB, normal=(0, 0, 1), back=TAB)]
    base_face = quad((0, 0, 0), (lx, 0, 0), (0, ly, 0), mix(W['c'], '#FFFFFF', 0.6))
    base_face = rotate([base_face], (0, 0, 0), (1, 0, 0), -125)
    return [walls + tabs, base_face], [((lx / 2, -40, -35), (lx / 2, -4, -6))]


def box_ring_open(W):
    """Drei Waende stehen, die vierte schwenkt mit der Lasche noch auf."""
    d, base = _bdec(W)
    lx, ly = BOX_W, BOX_D
    front, back, left, right = cuboid(0, 0, 0, lx, ly, 55, base, d, skip=('top', 'bottom'))
    left = rotate([left], (0, ly, 0), (0, 0, 1), -55)[0]
    tab = Face([(0, 0, 55), (0, 0, 0), (7, 2, 2), (7, 2, 53)], TAB, normal=(1, 0, 0), back=TAB)
    return [[back, right, front, tab, left]]


# ---------------------------------------------------------------- Waggon
def wagon_parts(W, ox=0.0):
    L, Wd, H = WG_L, WG_W, WG_H
    z0 = Z0
    P = dict(
        floor=quad((ox, 0, z0), (L, 0, 0), (0, Wd, 0), mix(W['c'], '#FFFFFF', 0.55)),
        wall_near=quad((ox, 0, z0 + H), (L, 0, 0), (0, 0, -H), W['c'], wagon_side(W, guides=False)),
        wall_far=quad((ox + L, Wd, z0 + H), (-L, 0, 0), (0, 0, -H), W['c'], wagon_side(W, guides=False)),
        end_left=quad((ox, Wd, z0 + H), (0, -Wd, 0), (0, 0, -H), W['c'], wagon_endwall(W)),
        end_right=quad((ox + L, 0, z0 + H), (0, Wd, 0), (0, 0, -H), W['c'], wagon_endwall(W)),
    )
    return P


def wheels_wagon(ox, side, y_off=0.0):
    r = WG_WHEEL_R
    x1, x2 = WG_WHEELS
    if side == 'near':
        return [disc_y(ox + x1, -0.8 + y_off, r, r, WOOD, wheel_decor(r)),
                disc_y(ox + x2, -0.8 + y_off, r, r, WOOD, wheel_decor(r))]
    return [disc_y(ox + x1, WG_W + 0.8, r, r, WOOD, wheel_decor(r), facing=1),
            disc_y(ox + x2, WG_W + 0.8, r, r, WOOD, wheel_decor(r), facing=1)]


def wagon_boxes(W, ox):
    """6 Kaestchen, 3 hintereinander (Tiefe 37) und 2 nebeneinander (Breite 42)."""
    lx, ly = BOX_D + T, BOX_W + T
    nums = list(range(6 * W['n'] - 5, 6 * W['n'] + 1))
    x0 = ox + (WG_L - 3 * lx) / 2
    y0 = (WG_W - 2 * ly) / 2
    out = []
    k = 0
    for j in range(2):
        for i in range(3):
            out.append((x0 + i * lx, y0 + (1 - j) * ly, nums[k]))
            k += 1
    return out, lx, ly


def wagon_model(W, ox=0.0, boxes=True, wheels=True, near=True, near_off=0.0):
    """near=False blendet die vordere lange Seitenwand (Teil B) aus, near_off schiebt sie nach vorn."""
    P = wagon_parts(W, ox)
    cam = Cam()
    g = []
    if wheels:
        g.append(wheels_wagon(ox, 'far'))
    g.append([P['floor'], P['wall_far'], P['end_left'], P['end_right']])
    if boxes:
        bx, lx, ly = wagon_boxes(W, ox)
        bx.sort(key=lambda t: -cam.depth((t[0] + lx / 2, t[1] + ly / 2, 70)))
        for x, y, num in bx:
            g.extend(box_closed(W, num, x, y, Z0 + 0.4, lx, ly))
    if near:
        g.append(move([P['wall_near']], (0, -near_off, 0)))
        if wheels:
            g.append(wheels_wagon(ox, 'near', near_off))
    return g


def wagon_A_only(W):
    P = wagon_parts(W)
    return [wheels_wagon(0, 'far'), [P['floor'], P['wall_far'], P['end_left'], P['end_right']]]


def wagon_B_only(W):
    P = wagon_parts(W)
    return [[P['wall_near']], wheels_wagon(0, 'near')]


# ---------------------------------------------------------------- Lok
def chassis(guides=False):
    d = dict(front=chassis_side(False), back=chassis_side(True), left=chassis_front, right=chassis_back)
    if guides:
        d['top'] = chassis_top
    return cuboid(0, 0, Z0, CH_L, CH_W, CH_H, LOCO['c'], d, skip=('bottom',), cols=dict(top=LOCO['d']))


def cab(lift=0.0):
    zc = Z0 + CH_H + lift
    y0 = (CH_W - CAB_B) / 2
    faces = cuboid(CH_L - CAB_A, y0, zc, CAB_A, CAB_B, CAB_H, LOCO['cream'],
                   dict(front=cab_side, back=cab_side, left=cab_front, right=cab_back), skip=('top', 'bottom'))
    faces.append(quad((CH_L - CAB_A, y0 + CAB_B, zc + CAB_H), (CAB_ROOF, 0, 0), (0, -CAB_B, 0), LOCO['d'], cab_roof,
                      back=LOCO['d']))
    return faces


BOILER_X0 = 10.0
BOILER_X1 = CH_L - CAB_A
BOILER_ZC = Z0 + CH_H + BOILER_R


def boiler(dx=0.0, dz=0.0, disc_off=0.0):
    x0, x1 = BOILER_X0 + dx, BOILER_X1 + dx
    bands = [(x0 + 4, x0 + 11, LOCO['boilerd']), (x0 + 60, x0 + 65, LOCO['boilerd']), (x1 - 8, x1, LOCO['boilerd'])]
    faces = cyl_x(x0, x1, CH_W / 2, BOILER_ZC + dz, BOILER_R, LOCO['boiler'], bands=bands,
                  cap0=None if disc_off else LOCO['cream'], cap_decor=None if disc_off else boiler_disc)
    extra = []
    if disc_off:
        r = BOILER_R + 0.5
        n = 40
        xd = x0 - disc_off
        pts = [(xd, CH_W / 2 + r * math.cos(2 * math.pi * i / n), BOILER_ZC + dz + r * math.sin(2 * math.pi * i / n)) for i in range(n)]
        extra.append(Face(pts, LOCO['cream'], normal=(-1, 0, 0),
                          frame=((xd, CH_W / 2 + r, BOILER_ZC + dz + r), (0, -2 * r, 0), (0, 0, -2 * r)), decor=boiler_disc))
        # Zacken vorne
        for i in range(16):
            a = 2 * math.pi * (i + 0.5) / 16
            cy, cz = CH_W / 2 + BOILER_R * math.cos(a), BOILER_ZC + dz + BOILER_R * math.sin(a)
            cy2, cz2 = CH_W / 2 + (BOILER_R - 7) * math.cos(a), BOILER_ZC + dz + (BOILER_R - 7) * math.sin(a)
            da = math.pi / 16 * 0.75
            p = lambda rr, aa: (x0, CH_W / 2 + rr * math.cos(aa), BOILER_ZC + dz + rr * math.sin(aa))
            extra.append(Face([p(BOILER_R, a - da), p(BOILER_R, a + da), p(BOILER_R - 7, a + da * 0.6), p(BOILER_R - 7, a - da * 0.6)],
                              TAB, normal=(-1, 0, 0), back=TAB))
    return faces, extra


CHIM_X = BOILER_X0 + 25


def chimney(lift=0.0):
    zb = BOILER_ZC + BOILER_R - 3 + lift
    return cyl_z(CHIM_X, CH_W / 2, zb, zb + 41, CHIM_R, LOCO['c'], top_col=mix(LOCO['d'], '#000000', 0.35),
                 bands=[(zb + 34, zb + 41, LOCO['d'])])


def cloud():
    pts = cloud_shape(0, 0, 1.15)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    cx, cz = CHIM_X + 22, BOILER_ZC + BOILER_R + 38 + 26
    p3 = [(cx + x, cz - y) for x, y in pts]
    return flat_y(p3, CH_W / 2 - 2, '#FFFFFF', cloud_decor, facing=-1,
                  box=(cx + min(xs), cz - min(ys), max(xs) - min(xs), max(ys) - min(ys)))


def loco_wheels(side, y_off=0.0, rods=True):
    zf, zr = LOCO_FRONT_R, LOCO_REAR_R
    if side == 'near':
        y = -0.8 - y_off
        f = [disc_y(45, y, zf, LOCO_FRONT_R, WOOD, wheel_decor(LOCO_FRONT_R)),
             disc_y(135, y, zr, LOCO_REAR_R, WOOD, wheel_decor(LOCO_REAR_R))]
        if rods:
            f.append(Face([(42, y - 0.8, zf + 2.5), (138, y - 0.8, zr + 2.5), (138, y - 0.8, zr - 2.5), (42, y - 0.8, zf - 2.5)],
                          WOOD2, normal=(0, -1, 0)))
        return f
    y = CH_W + 0.8
    return [disc_y(45, y, zf, LOCO_FRONT_R, WOOD, wheel_decor(LOCO_FRONT_R), facing=1),
            disc_y(135, y, zr, LOCO_REAR_R, WOOD, wheel_decor(LOCO_REAR_R), facing=1)]


def loco_model(stage=5):
    """stage: 1 Fahrgestell, 2 +Fuehrerhaus (schwebend), 3 Kessel einzeln, 4 +Kessel +Schornstein schwebend, 5 fertig"""
    g = []
    if stage == 3:
        b, extra = boiler(disc_off=30)
        return [b, extra], [((BOILER_X0 - 30 - 5, CH_W / 2, BOILER_ZC + 45), (BOILER_X0 - 4, CH_W / 2, BOILER_ZC + 40))]
    arrows = []
    g.append(loco_wheels('far'))
    g.append(chassis(guides=stage <= 2))
    if stage >= 2:
        lift = 45 if stage == 2 else 0
        g.append(cab(lift))
        if lift:
            arrows.append(((CH_L - CAB_A / 2, -20, Z0 + CH_H + lift + 20), (CH_L - CAB_A / 2, -20, Z0 + CH_H + 6)))
    if stage >= 4:
        b, _ = boiler()
        g.append(b)
        lift = 40 if stage == 4 else 0
        g.append(chimney(lift))
        if lift:
            arrows.append(((CHIM_X, -15, BOILER_ZC + BOILER_R + lift + 30), (CHIM_X, -15, BOILER_ZC + BOILER_R + 8)))
    if stage >= 5:
        g.append([cloud()])
        g.append(loco_wheels('near'))
    else:
        g.append(loco_wheels('near', rods=False))
    return g, arrows


# ---------------------------------------------------------------- ganzer Zug
GAP = 22.0


def coupling(x0, x1):
    return cuboid(x0, WG_W / 2 - 4, Z0 + 3, x1 - x0, 8, 5, WOODD)


def train_model(n_wagons=4, boxes=True):
    groups = []
    pos = []
    x = CH_L + GAP
    for W in WAGONS[:n_wagons]:
        pos.append((W, x))
        x += WG + GAP
    for W, ox in reversed(pos):
        groups.append(coupling(ox - GAP - 2, ox + 2))
        groups.extend(wagon_model(W, ox, boxes=boxes))
    lg, _ = loco_model(5)
    groups.extend([move(g, (0, (WG_W - CH_W) / 2, 0)) for g in lg])
    return groups
