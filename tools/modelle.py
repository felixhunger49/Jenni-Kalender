"""3D-Modelle von Kaestchen, Waggon und Lok fuer die Anleitungsbilder (Masse wie Vorlagen)."""
from iso import *
from zug import (WAGONS, LOCO, WOOD, WOOD2, WOODD, TAB, CREAM, CREAM2, BOILER_R, CHIM_R, CAB_A, CAB_B, CAB_H,
                 CAB_ROOF, CH_L, CH_W, CH_H, WG, WG_H, WG_LOW, WG_WHEEL_R, WG_WHEELS, LOCO_REAR_R, LOCO_FRONT_R,
                 wagon_side, wagon_endflap, wagon_endwall, box_wall, lid_top, wheel_decor,
                 chassis_side, chassis_front, chassis_back, chassis_top, cab_side, cab_front, cab_back, cab_roof,
                 boiler_disc, cloud_shape, cloud_decor, mix, chimney_profile)

Z0 = 8.0          # Bodenhoehe ueber dem Tisch (Raeder ragen 8 mm unter)
BOX_O = 56.0      # Unterteil aussen
BOX_HT = 56.0


# ---------------------------------------------------------------- Kaestchen
def box_bottom(W, x, y, z, open_top=True):
    deco, base = box_wall(W)
    d = dict(front=deco, back=deco, left=deco, right=deco)
    return cuboid(x, y, z, BOX_O, BOX_O, BOX_HT, base, d, skip=('top',) if open_top else ())


def box_closed(W, num, x, y, z):
    deco, base = box_wall(W)
    d = dict(front=deco, back=deco, left=deco, right=deco, top=lid_top(W, num))
    return [cuboid(x, y, z, BOX_O, BOX_O, BOX_HT, base, d, cols=dict(top=mix(W['c'], '#FFFFFF', 0.25)))]


def box_lid_open(W, num, ang=105, tuck=True):
    """Kaestchen mit aufgeklapptem Deckel (Scharnier an der Rueckwand)."""
    s = BOX_O
    lidc = mix(W['c'], '#FFFFFF', 0.25)
    walls = box_bottom(W, 0, 0, 0)
    top = quad((0, s, s), (s, 0, 0), (0, -s, 0), lidc, lid_top(W, num), back=lidc)
    parts = [top]
    if tuck:
        parts.append(quad((0, 0, s), (s, 0, 0), (0, 0, -12), lidc, back=lidc))
    parts = rotate(parts, (0, s, s), (1, 0, 0), -ang)
    dust = []
    for x, nx in ((0, -1), (s, 1)):
        dust.append(Face([(x, s, s), (x, 0, s), (x, 3, s + 12), (x, s - 16, s + 12)],
                         base_col(W), normal=(nx, 0, 0), back=base_col(W)))
    return [walls + dust, parts]


def base_col(W):
    return box_wall(W)[1]


def box_folding(W):
    """Waende stehen als Ring, Boden klappt noch auf."""
    deco, base = box_wall(W)
    s = BOX_O
    walls = cuboid(0, 0, 0, s, s, s, base, dict(front=deco, back=deco, left=deco, right=deco), skip=('top', 'bottom'))
    tabs = []
    t = 7
    tabs.append(Face([(0, 0, 0), (s, 0, 0), (s - 2, t, 0), (2, t, 0)], TAB, normal=(0, 0, 1), back=TAB))
    tabs.append(Face([(0, s, 0), (0, 0, 0), (t, 2, 0), (t, s - 2, 0)], TAB, normal=(0, 0, 1), back=TAB))
    tabs.append(Face([(s, s, 0), (0, s, 0), (2, s - t, 0), (s - 2, s - t, 0)], TAB, normal=(0, 0, 1), back=TAB))
    base_face = quad((0, 0, 0), (s, 0, 0), (0, s, 0), mix(W['c'], '#FFFFFF', 0.6))
    base_face = rotate([base_face], (0, 0, 0), (1, 0, 0), -125)
    return [walls + tabs, base_face], [((s / 2, -40, -38), (s / 2, -4, -6))]


def box_ring_open(W):
    """Drei Waende stehen, die vierte schwenkt mit der Lasche noch auf."""
    deco, base = box_wall(W)
    s = BOX_O
    f = cuboid(0, 0, 0, s, s, s, base, dict(front=deco, back=deco, left=deco, right=deco), skip=('top', 'bottom'))
    front, back, left, right = f
    left = rotate([left], (0, s, 0), (0, 0, 1), -55)[0]
    tab = Face([(0, 0, s), (0, 0, 0), (7, 2, 2), (7, 2, s - 2)], TAB, normal=(1, 0, 0), back=TAB)
    return [[back, right, front, tab, left]]


# ---------------------------------------------------------------- Waggon
def wagon_parts(W, ox=0.0):
    s, H, e = WG, WG_H, WG_LOW
    z0 = Z0
    A = dict(
        floor=quad((ox, 0, z0), (s, 0, 0), (0, s, 0), mix(W['c'], '#FFFFFF', 0.55)),
        side_near=quad((ox, 0, z0 + H), (s, 0, 0), (0, 0, -H), W['c'], wagon_side(W, guides=False)),
        side_far=quad((ox + s, s, z0 + H), (-s, 0, 0), (0, 0, -H), W['c'], wagon_side(W, guides=False)),
        flap_near=quad((ox, s, z0 + e), (0, -s, 0), (0, 0, -e), W['c'], wagon_endflap(W)),
        flap_far=quad((ox + s, 0, z0 + e), (0, s, 0), (0, 0, -e), W['c'], wagon_endflap(W)),
    )
    tabs = []
    for x, inward in ((ox, 1), (ox + s, -1)):
        for y, dy in ((0, 10), (s, -10)):
            tabs.append(Face([(x, y, z0 + H), (x, y + dy, z0 + H - 2.5), (x, y + dy, z0 + 5), (x, y, z0)],
                             TAB, normal=(-inward, 0, 0), back=TAB))
    A['tabs'] = tabs
    B = dict(
        top=quad((ox, s, z0 + e), (s, 0, 0), (0, -s, 0), INNER),
        end_near=quad((ox, s, z0 + H), (0, -s, 0), (0, 0, -(H - e)), W['c'], wagon_endwall(W)),
        end_far=quad((ox + s, 0, z0 + H), (0, s, 0), (0, 0, -(H - e)), W['c'], wagon_endwall(W)),
        leg_near=quad((ox, 0.6, z0 + e), (s, 0, 0), (0, 0, -e), CREAM2, back=CREAM2),
        leg_far=quad((ox + s, s - 0.6, z0 + e), (-s, 0, 0), (0, 0, -e), CREAM2, back=CREAM2),
    )
    return A, B


def wheels_wagon(ox, side, y_off=0.0):
    r = WG_WHEEL_R
    zc = r
    x1, x2 = WG_WHEELS
    if side == 'near':
        return [disc_y(ox + x1, -0.8 + y_off, zc, r, WOOD, wheel_decor(r)),
                disc_y(ox + x2, -0.8 + y_off, zc, r, WOOD, wheel_decor(r))]
    return [disc_y(ox + x1, WG + 0.8, zc, r, WOOD, wheel_decor(r), facing=1),
            disc_y(ox + x2, WG + 0.8, zc, r, WOOD, wheel_decor(r), facing=1)]


def wagon_boxes(W, ox):
    nums = list(range(4 * W['n'] - 3, 4 * W['n'] + 1))
    groups = []
    k = 0
    for j in range(2):
        for i in range(2):
            x = ox + 3 + i * (BOX_O + 2)
            y = 3 + (1 - j) * (BOX_O + 2)
            groups.append((x, y, nums[k]))
            k += 1
    return groups


def wagon_model(W, ox=0.0, boxes=True, wheels=True, B_lift=None, wheel_out=0.0):
    A, B = wagon_parts(W, ox)
    cam = Cam()
    g = []
    if wheels:
        g.append(wheels_wagon(ox, 'far'))
    back = [A['floor'], A['side_far'], A['flap_far']]
    if B_lift is None:
        back += [B['top'], B['end_far']]
    else:
        back += A['tabs']
    g.append(back)
    if boxes:
        bx = wagon_boxes(W, ox)
        bx.sort(key=lambda t: -cam.depth((t[0] + 29, t[1] + 29, 70)))
        for x, y, num in bx:
            g.extend(box_closed(W, num, x, y, Z0 + WG_LOW + 0.4))
    front = [A['side_near'], A['flap_near']]
    if B_lift is None:
        front.append(B['end_near'])
    g.append(front)
    if B_lift is not None:
        lift = (0, 0, B_lift)
        g.append(move([B['leg_far'], B['top'], B['end_far'], B['leg_near'], B['end_near']], lift))
    if wheels:
        g.append(wheels_wagon(ox, 'near', -wheel_out))
    return g


def wagon_A_only(W):
    A, B = wagon_parts(W)
    return [wheels_wagon(0, 'far'), [A['floor'], A['side_far'], A['flap_far']] + A['tabs'],
            [A['side_near'], A['flap_near']], wheels_wagon(0, 'near')]


def wagon_B_only(W):
    A, B = wagon_parts(W)
    faces = [B['top'], B['end_far'], B['end_near'], B['leg_near'], B['leg_far']]
    return [move(faces, (0, 0, 10))]


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
    return cuboid(x0, WG / 2 - 4, Z0 + 3, x1 - x0, 8, 5, WOODD)


def train_model(n_wagons=6, boxes=True):
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
    groups.extend([move(g, (0, (WG - CH_W) / 2, 0)) for g in lg])
    return groups
