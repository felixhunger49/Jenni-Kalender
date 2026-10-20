"""Geometrie, Dekor und Bastelteile fuer den Eisenbahn-Adventskalender.

Alle Masse in Millimetern. Jedes Bastelteil (Part) besteht aus Flaechen
(Polygonen). Gemeinsame Kanten zweier Flaechen werden automatisch zu
Falzlinien, alle uebrigen Kanten zu Schnittlinien.
"""
import base64
import glob
import io
import math
import os

TIER_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tiere')

# ---------------------------------------------------------------- Farben
INK = '#5A4636'
CUT = '#3B3027'
FOLD = '#8A7A6A'
TAB = '#E6E0D6'
CREAM = '#F4ECDF'
CREAM2 = '#FBF6EE'
WOOD = '#8A6A50'
WOOD2 = '#A9865F'
WOODD = '#6E523C'
STAR = '#E3C68E'
TREE = '#93A486'
TREED = '#6E8265'
PINK = '#E9B4A8'
WHITE = '#FFFFFF'

WAGONS = [
    dict(n=1, animal='loewe', name='Löwe', c='#B7C3A5', d='#8C9B79', acc='#EAD3B5', scarf='#C98E6E'),
    dict(n=2, animal='baer', name='Bär', c='#E6C0B4', d='#C39386', acc='#F5E4DA', scarf='#9DB3C2'),
    dict(n=3, animal='hase', name='Hase', c='#E8DBC5', d='#C1AB89', acc='#F6EEE1', scarf='#B7C3A5'),
    dict(n=4, animal='pinguin', name='Pinguin', c='#BCCDD9', d='#8CA3B4', acc='#E6EDF2', scarf='#E2A69A'),
    dict(n=5, animal='otter', name='Otter', c='#C3CCA8', d='#96A17A', acc='#EDEFE0', scarf='#D9B48A'),
    dict(n=6, animal='giraffe', name='Giraffe', c='#EFE0C9', d='#D1B38E', acc='#F1D3CB', scarf='#B5C7D3'),
]
LOCO = dict(c='#B7C3A5', d='#8C9B79', boiler='#E8C4BA', boilerd='#C49A8E', cream='#F3EADB',
            scarf='#9DB3C2')

FONT_HAND = "'Patrick Hand', 'Hand', 'Comic Sans MS', cursive"
FONT_TXT = "'Nunito', 'Liberation Sans', Arial, sans-serif"

# ---------------------------------------------------------------- Masse
BOX = 55.0          # Kaestchen innen (Kantenlaenge)
BOX_TAB = 8.0
LID = 57.0          # Deckel innen
LID_H = 18.0        # Deckelrand
WG = 120.0          # Waggon innen (Laenge = Breite)
WG_H = 80.0         # Waggon Wandhoehe
WG_LOW = 35.0       # Hoehe Zwischenboden (Stirnklappe Teil A)
WG_B = 119.0        # Teil B (etwas kleiner, passt in Teil A)
WG_WHEEL_R = 20.0
WHEEL_DROP = 8.0    # so weit ragen alle Raeder unter den Boden
CH_L, CH_W, CH_H = 180.0, 90.0, 30.0       # Lok-Fahrgestell
CAB_A, CAB_B, CAB_H = 60.0, 75.0, 95.0     # Fuehrerhaus (laengs, quer, hoch)
CAB_ROOF = 70.0                            # Dach (mit Ueberstand nach hinten)
BOILER_R = 32.5
BOILER_L = 110.0
CHIM_R = 12.0
CHIM_H = 40.0
LOCO_REAR_R, LOCO_FRONT_R = 24.0, 17.0


def mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02X%02X%02X' % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def f(v):
    s = ('%.2f' % v).rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


def pts_str(pts):
    return ' '.join('%s,%s' % (f(x), f(y)) for x, y in pts)


# ---------------------------------------------------------------- Dekor-Primitive
def star(cx, cy, r, fill=STAR, rot=0):
    p = []
    for i in range(10):
        a = math.radians(rot - 90 + i * 36)
        rr = r if i % 2 == 0 else r * 0.47
        p.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return ('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>'
            % (pts_str(p), fill, fill, f(r * 0.18)))


def dot(cx, cy, r, fill):
    return '<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (f(cx), f(cy), f(r), fill)


def tree(cx, by, h, col=TREE, dark=TREED, snow=False):
    w = h * 0.62
    out = ['<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (
        f(cx - h * 0.05), f(by - h * 0.14), f(h * 0.1), f(h * 0.14), WOOD2)]
    tiers = [(0.86, 0.0, 1.0), (0.62, 0.27, 0.8), (0.4, 0.52, 0.58)]
    for i, (b, t, sc) in enumerate(tiers):
        yb = by - h * 0.12 - h * t * 0.95
        yt = yb - h * 0.42
        ww = w * sc / 2
        c = col if i % 2 == 0 else dark
        out.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (
            pts_str([(cx - ww, yb), (cx, yt), (cx + ww, yb)]), c, c, f(h * 0.05)))
    out.append(star(cx, by - h * 1.0, h * 0.09))
    if snow:
        for i in range(5):
            out.append(dot(cx - w * 0.25 + i * w * 0.12, by - h * (0.3 + 0.12 * (i % 3)), h * 0.018, WHITE))
    return ''.join(out)


def sprig(cx, cy, s, col=TREE, rot=0):
    out = ['<g transform="translate(%s,%s) rotate(%s) scale(%s)">' % (f(cx), f(cy), f(rot), f(s / 10))]
    out.append('<path d="M0,6 Q0.5,0 0,-6" stroke="%s" stroke-width="0.7" fill="none"/>' % col)
    for y, side in ((3, -1), (0, 1), (-3, -1), (1.5, -1), (-1.5, 1)):
        out.append('<ellipse cx="%s" cy="%s" rx="2.1" ry="1" fill="%s" transform="rotate(%s %s %s)"/>' % (
            f(side * 1.9), f(y), col, f(-30 * side), f(side * 1.9), f(y)))
    out.append('</g>')
    return ''.join(out)


def heart(cx, cy, s, fill=PINK):
    return ('<path d="M%s,%s C%s,%s %s,%s %s,%s C%s,%s %s,%s %s,%s Z" fill="%s"/>' % (
        f(cx), f(cy + s * 0.45),
        f(cx - s * 0.9), f(cy - s * 0.1), f(cx - s * 0.45), f(cy - s * 0.75), f(cx), f(cy - s * 0.25),
        f(cx + s * 0.45), f(cy - s * 0.75), f(cx + s * 0.9), f(cy - s * 0.1), f(cx), f(cy + s * 0.45), fill))


def gift(cx, by, s, col=PINK, ribbon=CREAM2):
    w = s
    h = s * 0.8
    return ''.join([
        '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="%s"/>' % (f(cx - w / 2), f(by - h), f(w), f(h), f(s * 0.06), col),
        '<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (f(cx - w * 0.08), f(by - h), f(w * 0.16), f(h), ribbon),
        '<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (f(cx - w / 2), f(by - h * 0.62), f(w), f(h * 0.14), ribbon),
        '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="none" stroke="%s" stroke-width="%s"/>' % (
            f(cx - s * 0.17), f(by - h - s * 0.1), f(s * 0.17), f(s * 0.1), ribbon, f(s * 0.08)),
        '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="none" stroke="%s" stroke-width="%s"/>' % (
            f(cx + s * 0.17), f(by - h - s * 0.1), f(s * 0.17), f(s * 0.1), ribbon, f(s * 0.08)),
    ])


def bunting(x0, x1, y, n, cols, s=5):
    out = ['<path d="M%s,%s Q%s,%s %s,%s" stroke="%s" stroke-width="0.4" fill="none"/>' % (
        f(x0), f(y), f((x0 + x1) / 2), f(y + s * 0.5), f(x1), f(y), WOOD2)]
    for i in range(n):
        t = (i + 0.5) / n
        x = x0 + (x1 - x0) * t
        yy = y + s * 0.5 * 4 * t * (1 - t) * 0.5
        out.append('<polygon points="%s" fill="%s"/>' % (pts_str(
            [(x - s * 0.4, yy), (x + s * 0.4, yy), (x, yy + s)]), cols[i % len(cols)]))
    return ''.join(out)


def text(x, y, s, size, fill=INK, anchor='middle', font=FONT_TXT, weight='normal', extra=''):
    s = s.replace('&', '&amp;').replace('<', '&lt;')
    return ('<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="%s" fill="%s" text-anchor="%s" %s>%s</text>'
            % (f(x), f(y), font, f(size), weight, fill, anchor, extra, s))


def arch_path(cx, top, w, h):
    r = w / 2
    x0, x1 = cx - r, cx + r
    return 'M%s,%s L%s,%s A%s,%s 0 0 1 %s,%s L%s,%s Z' % (
        f(x0), f(top + h), f(x0), f(top + r), f(r), f(r), f(x1), f(top + r), f(x1), f(top + h))


# ---------------------------------------------------------------- Tiergesichter
def _eyes(dx, ey, r=3.6):
    o = []
    for sx in (-1, 1):
        o.append(dot(sx * dx, ey, r, '#3A2C24'))
        o.append(dot(sx * dx + r * 0.35, ey - r * 0.35, r * 0.33, WHITE))
    return ''.join(o)


def _blush(dx, y, r=4.5):
    return ''.join('<circle cx="%s" cy="%s" r="%s" fill="#E99A8E" opacity="0.55"/>' % (f(sx * dx), f(y), f(r))
                   for sx in (-1, 1))


def _scarf(col):
    return ('<path d="M-25,27 Q0,36 25,27 L26,35 Q0,44 -26,35 Z" fill="%s"/>'
            '<path d="M10,36 L17,52 L8,53 L4,38 Z" fill="%s"/>'
            '<path d="M-25,29 Q0,38 25,29" stroke="%s" stroke-width="1.2" fill="none" opacity="0.5"/>'
            % (col, mix(col, '#000000', 0.12), WHITE))


def _hat(col, band=CREAM2):
    return ('<path d="M-28,-13 Q-27,-44 0,-45 Q27,-44 28,-13 Z" fill="%s"/>'
            '<rect x="-30" y="-19" width="60" height="9" rx="4.5" fill="%s"/>'
            '<circle cx="0" cy="-47" r="7" fill="%s"/>'
            '<path d="M-14,-40 L-14,-21 M-5,-44 L-5,-21 M5,-44 L5,-21 M14,-40 L14,-21" stroke="%s" stroke-width="1.2" opacity="0.35"/>'
            % (col, band, band, mix(col, '#000000', 0.3)))


def animal(kind, scarf='#9DB3C2', hat=None):
    """Gesicht im 100er-Raster, Kopf-Mittelpunkt (0,0), Kopfradius ca. 30."""
    o = []
    dark = '#3A2C24'
    if kind == 'fuchs':
        body = '#D9874E'
        for sx in (-1, 1):
            o.append('<polygon points="%s" fill="%s"/>' % (pts_str([(sx * 29, -6), (sx * 23, -48), (sx * 3, -24)]), body))
            o.append('<polygon points="%s" fill="#6E4A34"/>' % pts_str([(sx * 24, -14), (sx * 22, -40), (sx * 10, -24)]))
        o.append(_scarf(scarf))
        o.append('<ellipse cx="0" cy="0" rx="31" ry="28" fill="%s"/>' % body)
        o.append('<path d="M-31,2 Q-20,26 0,24 Q20,26 31,2 Q20,6 12,4 Q0,14 -12,4 Q-20,6 -31,2 Z" fill="#FBF3E8"/>')
        o.append(_eyes(11, -3))
        o.append('<ellipse cx="0" cy="9" rx="4.2" ry="3" fill="%s"/>' % dark)
        o.append('<path d="M-4,14 Q0,17 0,13 Q0,17 4,14" stroke="%s" stroke-width="1.2" fill="none"/>' % dark)
        o.append(_blush(20, 6))
    elif kind == 'loewe':
        mane = '#C98A4B'
        for i in range(14):
            a = 2 * math.pi * i / 14
            o.append(dot(32 * math.cos(a), 32 * math.sin(a) - 1, 11, mane))
        o.append(dot(0, -1, 36, mane))
        o.append(_scarf(scarf))
        for sx in (-1, 1):
            o.append(dot(sx * 20, -21, 7.5, '#E8B66E'))
            o.append(dot(sx * 20, -21, 4, '#D29558'))
        o.append(dot(0, 0, 27, '#E8B66E'))
        o.append('<ellipse cx="0" cy="11" rx="13" ry="9" fill="#F6E3C2"/>')
        o.append(_eyes(10, -4))
        o.append('<path d="M-5,5 L5,5 L0,10 Z" fill="#7A4E36" stroke="#7A4E36" stroke-linejoin="round" stroke-width="2"/>')
        o.append('<path d="M-5,14 Q0,17 0,11 Q0,17 5,14" stroke="%s" stroke-width="1.2" fill="none"/>' % dark)
        o.append(_blush(17, 7))
    elif kind in ('baer', 'otter'):
        if kind == 'baer':
            body, inner, muz, er, ey = '#A47A58', '#D2AC88', '#E5C9A9', 10, -22
        else:
            body, inner, muz, er, ey = '#9C7859', '#C9A486', '#EBD8C0', 6.5, -18
        for sx in (-1, 1):
            o.append(dot(sx * 22, ey, er, body))
            o.append(dot(sx * 22, ey, er * 0.55, inner))
        o.append(_scarf(scarf))
        o.append(dot(0, 0, 30, body))
        if kind == 'otter':
            o.append('<ellipse cx="0" cy="10" rx="17" ry="11" fill="%s"/>' % muz)
            for sx in (-1, 1):
                for k in range(3):
                    o.append(dot(sx * (7 + k * 3.5), 12 + (k % 2) * 2, 0.9, '#7A5C45'))
        else:
            o.append('<ellipse cx="0" cy="10" rx="13" ry="10" fill="%s"/>' % muz)
        o.append(_eyes(11, -4))
        o.append('<ellipse cx="0" cy="5" rx="5" ry="3.6" fill="%s"/>' % dark)
        o.append('<path d="M-4,12 Q0,15 0,9 Q0,15 4,12" stroke="%s" stroke-width="1.2" fill="none"/>' % dark)
        o.append(_blush(19, 7))
    elif kind == 'hase':
        body = '#C7B29C'
        for sx in (-1, 1):
            o.append('<ellipse cx="%s" cy="-40" rx="7.5" ry="22" fill="%s" transform="rotate(%s %s -40)"/>' % (
                f(sx * 11), body, f(sx * 9), f(sx * 11)))
            o.append('<ellipse cx="%s" cy="-39" rx="3.6" ry="15" fill="#EDBDB3" transform="rotate(%s %s -40)"/>' % (
                f(sx * 11), f(sx * 9), f(sx * 11)))
        o.append(_scarf(scarf))
        o.append(dot(0, 0, 28, body))
        o.append(dot(-5, 10, 6.5, '#F6EEE3'))
        o.append(dot(5, 10, 6.5, '#F6EEE3'))
        o.append(_eyes(10, -4))
        o.append('<path d="M-3.5,4 L3.5,4 L0,8 Z" fill="#D98C82" stroke="#D98C82" stroke-linejoin="round" stroke-width="1.5"/>')
        o.append(_blush(17, 6))
    elif kind == 'pinguin':
        body = '#4F5C6C'
        o.append(_scarf(scarf))
        o.append(dot(0, 0, 30, body))
        o.append(dot(-10, 3, 15, '#FAF6F0'))
        o.append(dot(10, 3, 15, '#FAF6F0'))
        o.append('<ellipse cx="0" cy="12" rx="17" ry="13" fill="#FAF6F0"/>')
        o.append(_eyes(9, -1))
        o.append('<path d="M-5,7 L5,7 L0,14 Z" fill="#E8A15A" stroke="#E8A15A" stroke-linejoin="round" stroke-width="2"/>')
        o.append(_blush(17, 9))
    elif kind == 'giraffe':
        body = '#EDCB80'
        for sx in (-1, 1):
            o.append('<path d="M%s,-24 L%s,-44" stroke="#C99A5C" stroke-width="4.5" stroke-linecap="round"/>' % (f(sx * 9), f(sx * 12)))
            o.append(dot(sx * 12, -45, 5, '#9C6B3E'))
            o.append('<ellipse cx="%s" cy="-14" rx="11" ry="5" fill="%s" transform="rotate(%s %s -14)"/>' % (
                f(sx * 28), body, f(sx * 20), f(sx * 28)))
            o.append('<ellipse cx="%s" cy="-14" rx="6" ry="2.4" fill="#E2A880" transform="rotate(%s %s -14)"/>' % (
                f(sx * 28), f(sx * 20), f(sx * 28)))
        o.append(_scarf(scarf))
        o.append('<ellipse cx="0" cy="0" rx="25" ry="30" fill="%s"/>' % body)
        for x, y, r in ((-16, -14, 4), (15, -17, 3.5), (-19, 3, 3), (18, 2, 3.4), (-6, -24, 2.6), (8, -26, 2.4)):
            o.append(dot(x, y, r, '#D9A55A'))
        o.append('<ellipse cx="0" cy="15" rx="17" ry="12" fill="#F5E2B6"/>')
        o.append(dot(-5, 13, 1.6, '#8A6243'))
        o.append(dot(5, 13, 1.6, '#8A6243'))
        o.append(_eyes(10, -5))
        o.append('<path d="M-4,20 Q0,23 4,20" stroke="%s" stroke-width="1.2" fill="none"/>' % dark)
        o.append(_blush(17, 5))
    if hat:
        o.append(_hat(hat))
    return '<g>%s</g>' % ''.join(o)


ANIMAL_HATS = {'baer': '#9DB3C2', 'pinguin': '#C98E6E', 'otter': '#B7C3A5', 'fuchs': '#B7C3A5'}


def animal_at(kind, cx, cy, size, scarf):
    """size = Kopfdurchmesser in mm"""
    s = size / 60.0
    return '<g transform="translate(%s,%s) scale(%s)">%s</g>' % (
        f(cx), f(cy), f(s), animal(kind, scarf, ANIMAL_HATS.get(kind)))


# ---------------------------------------------------------------- Dekor der Flaechen
_clip_id = [0]


def clip_uid():
    _clip_id[0] += 1
    return 'c%d' % _clip_id[0]


_img_cache = {}


def animal_image(kind):
    """Eigenes Tierbild (z.B. aus ComfyUI) als data-URI, falls tiere/<kind>*.png|jpg existiert."""
    if kind in _img_cache:
        return _img_cache[kind]
    uri = None
    files = sorted(glob.glob(os.path.join(TIER_DIR, '*%s*.png' % kind)) + glob.glob(os.path.join(TIER_DIR, '*%s*.jp*g' % kind)))
    if files:
        path = files[-1]
        try:
            from PIL import Image
            im = Image.open(path).convert('RGB')
            im.thumbnail((700, 700))
            buf = io.BytesIO()
            im.save(buf, 'JPEG', quality=88)
            uri = 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()
        except ImportError:
            mime = 'image/png' if path.endswith('.png') else 'image/jpeg'
            uri = 'data:%s;base64,%s' % (mime, base64.b64encode(open(path, 'rb').read()).decode())
    _img_cache[kind] = uri
    return uri


def window_with_animal(cx, top, w, h, kind, scarf, frame=CREAM2, inner='#F8F1E6'):
    cid = clip_uid()
    p = arch_path(cx, top, w, h)
    img = animal_image(kind)
    if img:
        return ''.join([
            '<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, p),
            '<path d="%s" fill="%s"/>' % (p, inner),
            '<image href="%s" x="%s" y="%s" width="%s" height="%s" preserveAspectRatio="xMidYMid slice" clip-path="url(#%s)"/>' % (
                img, f(cx - w / 2), f(top), f(w), f(h), cid),
            '<path d="%s" fill="none" stroke="%s" stroke-width="%s"/>' % (p, frame, f(w * 0.06)),
        ])
    return ''.join([
        '<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, p),
        '<path d="%s" fill="%s"/>' % (p, inner),
        '<g clip-path="url(#%s)">' % cid,
        '<rect x="%s" y="%s" width="%s" height="%s" fill="%s" opacity="0.5"/>' % (f(cx - w / 2), f(top + h * 0.72), f(w), f(h), mix(inner, WOOD2, 0.25)),
        animal_at(kind, cx, top + h * 0.5, w * 0.55, scarf),
        '</g>',
        '<path d="%s" fill="none" stroke="%s" stroke-width="%s"/>' % (p, frame, f(w * 0.06)),
    ])


def wheel_guide(cx, cy, r):
    return ('<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="0.35" stroke-dasharray="1.2,1.2" opacity="0.8"/>'
            % (f(cx), f(cy), f(r), WOODD))


def wagon_side(W, guides=True):
    def d(w, h):
        o = []
        o.append('<rect x="0" y="%s" width="%s" height="%s" fill="%s"/>' % (f(h - 12), f(w), f(12), W['d']))
        o.append('<rect x="0" y="%s" width="%s" height="1" fill="%s" opacity="0.8"/>' % (f(h - 13), f(w), CREAM2))
        for x in range(6, int(w), 12):
            o.append(dot(x, h - 6, 0.9, mix(W['d'], '#000000', 0.25)))
        o.append(tree(15, 46, 30, mix(TREE, W['d'], 0.3), TREED, snow=True))
        o.append(tree(105, 46, 30, mix(TREE, W['d'], 0.3), TREED, snow=True))
        for x, y, r in ((6, 10, 2.4), (114, 10, 2.4), (28, 8, 2), (92, 8, 2), (5, 40, 1.6), (115, 40, 1.6),
                        (27, 38, 1.6), (93, 38, 1.6)):
            o.append(star(x, y, r, STAR if r > 1.8 else CREAM2))
        o.append(window_with_animal(60, 5, 50, 42, W['animal'], W['scarf']))
        o.append('<rect x="31" y="46" width="58" height="4.5" rx="2" fill="%s"/>' % CREAM2)
        o.append(bunting(34, 86, 50.5, 7, [W['d'], CREAM2, PINK], 4))
        o.append(gift(60, 66, 9, PINK if W['n'] != 2 else W['acc']))
        if guides:
            o.append(wheel_guide(28, h - 12, WG_WHEEL_R))
            o.append(wheel_guide(92, h - 12, WG_WHEEL_R))
        return ''.join(o)
    return d


def wagon_endflap(W):
    def d(w, h):
        o = ['<rect x="0" y="%s" width="%s" height="12" fill="%s"/>' % (f(h - 12), f(w), W['d']),
             '<rect x="0" y="%s" width="%s" height="1" fill="%s" opacity="0.8"/>' % (f(h - 13), f(w), CREAM2),
             '<rect x="%s" y="%s" width="16" height="7" rx="1.5" fill="%s"/>' % (f(w / 2 - 8), f(h - 10), WOODD),
             dot(w / 2, h - 6.5, 1.6, WOOD2)]
        for x in (14, 34, 86, 106):
            o.append(star(x, 9, 2.2, STAR))
        o.append(heart(w / 2, 10, 6, PINK))
        return ''.join(o)
    return d


def wagon_endwall(W):
    def d(w, h):
        o = [bunting(6, w - 6, 3, 11, [W['d'], CREAM2, PINK, STAR], 6)]
        o.append(tree(22, h - 4, 26, mix(TREE, W['d'], 0.3), TREED, snow=True))
        o.append(tree(w - 22, h - 4, 26, mix(TREE, W['d'], 0.3), TREED, snow=True))
        o.append('<circle cx="%s" cy="%s" r="13" fill="%s"/>' % (f(w / 2), f(h / 2 + 4), CREAM2))
        o.append(text(w / 2, h / 2 + 10.5, str(W['n']), 17, W['d'], font=FONT_HAND))
        for x, y in ((42, 20), (78, 20), (40, 38), (80, 38)):
            o.append(star(x, y, 1.8, STAR))
        return ''.join(o)
    return d


def plain_label(lines, col=INK, size=4.2, opacity=0.75):
    def d(w, h):
        o = []
        n = len(lines)
        for i, ln in enumerate(lines):
            sz = size * (1.5 if i == 0 else 1)
            o.append(text(w / 2, h / 2 + (i - (n - 1) / 2) * size * 1.9 + sz * 0.35, ln, sz, col,
                          font=FONT_HAND if i == 0 else FONT_TXT, extra='opacity="%s"' % opacity))
        return ''.join(o)
    return d


def wheel_decor(r, col=WOOD):
    def d(w, h):
        cx, cy = w / 2, h / 2
        o = [dot(cx, cy, r, col),
             '<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="%s"/>' % (
                 f(cx), f(cy), f(r * 0.8), WOOD2, f(r * 0.1)),
             dot(cx, cy, r * 0.52, mix(col, '#000000', 0.1))]
        for i in range(10):
            a = 2 * math.pi * i / 10
            o.append(dot(cx + r * 0.66 * math.cos(a), cy + r * 0.66 * math.sin(a), r * 0.045, CREAM2))
        o.append(dot(cx, cy, r * 0.36, CREAM))
        o.append(star(cx, cy, r * 0.28, WOOD2))
        o.append(dot(cx, cy, r * 0.07, CREAM))
        return ''.join(o)
    return d


def hub_decor(r):
    def d(w, h):
        cx, cy = w / 2, h / 2
        return dot(cx, cy, r, CREAM) + '<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="0.6"/>' % (
            f(cx), f(cy), f(r * 0.85), WOOD2) + star(cx, cy, r * 0.65, WOOD2) + dot(cx, cy, r * 0.15, CREAM)
    return d


def box_wall(W):
    base = mix(W['c'], WHITE, 0.45)

    def d(w, h):
        o = []
        o.append(tree(w * 0.78, h - 6, 20, mix(TREE, W['d'], 0.3), TREED))
        for x, y, r in ((10, 12, 2.4), (24, 30, 1.8), (12, 42, 1.6), (36, 14, 1.6), (44, 26, 2.2)):
            o.append(star(x, y, r, STAR if r > 2 else W['d']))
        o.append(sprig(12, h - 10, 9, mix(TREE, W['d'], 0.3), -20))
        return ''.join(o)
    return d, base


def lid_top(W, num):
    def d(w, h):
        o = ['<rect x="4" y="4" width="%s" height="%s" rx="4" fill="%s"/>' % (f(w - 8), f(h - 8), CREAM2),
             '<rect x="6" y="6" width="%s" height="%s" rx="3" fill="none" stroke="%s" stroke-width="0.6" stroke-dasharray="1.6,1.2"/>' % (
                 f(w - 12), f(h - 12), W['d']),
             text(w / 2, h / 2 + 11, str(num), 32, INK, font=FONT_HAND)]
        o.append(sprig(11, 11, 8, mix(TREE, W['d'], 0.3), 40))
        o.append(sprig(w - 11, h - 11, 8, mix(TREE, W['d'], 0.3), 220))
        o.append(star(w - 11, 11, 2.4))
        o.append(star(11, h - 11, 2.4))
        return ''.join(o)
    return d


def lid_wall(W, num):
    def d(w, h):
        o = []
        for i, x in enumerate(range(5, int(w), 9)):
            o.append(star(x, h / 2 + (2 if i % 2 else -2), 1.7, CREAM2 if i % 2 else STAR))
        return ''.join(o)
    return d


# ---- Lok
def chassis_side(mirror):
    def d(w, h):
        o = ['<rect x="0" y="0" width="%s" height="2.5" fill="%s"/>' % (f(w), LOCO['cream'])]
        for x in range(8, int(w), 10):
            o.append(dot(x, 6.5, 1, mix(LOCO['d'], '#000000', 0.25)))
        o.append('<rect x="0" y="%s" width="%s" height="1.5" fill="%s" opacity="0.6"/>' % (f(h - 3), f(w), LOCO['cream']))
        front, rear = (w - 45, w - 135) if mirror else (45, 135)
        o.append(wheel_guide(front, h + WHEEL_DROP - LOCO_FRONT_R, LOCO_FRONT_R))
        o.append(wheel_guide(rear, h + WHEEL_DROP - LOCO_REAR_R, LOCO_REAR_R))
        return ''.join(o)
    return d


def chassis_front(w, h):
    o = ['<rect x="0" y="0" width="%s" height="2.5" fill="%s"/>' % (f(w), LOCO['cream'])]
    # Schienenraeumer
    o.append('<path d="M%s,%s L%s,%s L%s,%s L%s,%s Z" fill="%s"/>' % (
        f(14), f(12), f(w - 14), f(12), f(w - 6), f(h), f(6), f(h), WOODD))
    for i in range(7):
        x = 14 + i * (w - 28) / 6
        o.append('<path d="M%s,12 L%s,%s" stroke="%s" stroke-width="1.6"/>' % (f(x), f(6 + i * (w - 12) / 6), f(h), WOOD2))
    for x in (12, w - 12):
        o.append(dot(x, 7, 3.6, STAR))
        o.append(dot(x, 7, 2, CREAM2))
    o.append(heart(w / 2, 7, 4.5, PINK))
    return ''.join(o)


def chassis_back(w, h):
    o = ['<rect x="0" y="0" width="%s" height="2.5" fill="%s"/>' % (f(w), LOCO['cream']),
         '<rect x="%s" y="%s" width="16" height="7" rx="1.5" fill="%s"/>' % (f(w / 2 - 8), f(h - 12), WOODD)]
    for x in (14, w - 14):
        o.append(star(x, 13, 2.4))
    return ''.join(o)


def chassis_top(w, h):
    o = ['<rect x="10" y="%s" width="110" height="%s" fill="none" stroke="%s" stroke-width="0.5" stroke-dasharray="2,1.5"/>' % (
        f(h / 2 - 15), f(30), LOCO['cream']),
        text(65, h / 2 + 1.8, 'Kessel hier aufkleben', 5, LOCO['cream']),
        '<rect x="120" y="%s" width="%s" height="%s" fill="none" stroke="%s" stroke-width="0.5" stroke-dasharray="2,1.5"/>' % (
            f((h - CAB_B) / 2), f(CAB_A), f(CAB_B), LOCO['cream']),
        text(150, h / 2 - 2, 'Führerhaus', 5, LOCO['cream']),
        text(150, h / 2 + 5, 'hier', 5, LOCO['cream']),
        text(4, 7, '◄ vorne', 4, LOCO['cream'], anchor='start')]
    return ''.join(o)


def cab_side(w, h):
    o = ['<rect x="0" y="%s" width="%s" height="10" fill="%s"/>' % (f(h - 10), f(w), LOCO['d'])]
    o.append(window_with_animal(w / 2, 10, 40, 40, 'fuchs', LOCO['scarf']))
    o.append('<rect x="%s" y="49" width="46" height="4.5" rx="2" fill="%s"/>' % (f(w / 2 - 23), CREAM2))
    o.append(tree(14, h - 13, 22, TREE, TREED, snow=True))
    o.append(gift(w - 15, h - 13, 12, PINK))
    for x, y, r in ((8, 8, 2.2), (w - 8, 8, 2.2), (w / 2, 62, 2.4), (6, 56, 1.6), (w - 6, 58, 1.6)):
        o.append(star(x, y, r))
    return ''.join(o)


def cab_front(w, h):
    o = []
    for x in (w / 2 - 18, w / 2 + 18):
        o.append(dot(x, 16, 9, CREAM2))
        o.append(dot(x, 16, 7, '#F8F1E6'))
        o.append('<path d="M%s,16 L%s,16 M%s,9 L%s,23" stroke="%s" stroke-width="1"/>' % (
            f(x - 7), f(x + 7), f(x), f(x), CREAM2))
    o.append(star(w / 2, 16, 3))
    o.append('<rect x="0" y="%s" width="%s" height="10" fill="%s"/>' % (f(h - 10), f(w), LOCO['d']))
    o.append(text(w / 2, 50, '(vom Kessel verdeckt)', 3.6, mix(LOCO['c'], '#000000', 0.3)))
    return ''.join(o)


def cab_back(w, h):
    o = ['<rect x="0" y="%s" width="%s" height="10" fill="%s"/>' % (f(h - 10), f(w), LOCO['d']),
         '<path d="%s" fill="%s"/>' % (arch_path(w / 2, 22, 30, 63), LOCO['d']),
         '<path d="%s" fill="%s"/>' % (arch_path(w / 2, 26, 22, 22), '#F8F1E6'),
         dot(w / 2 + 9, 62, 1.6, STAR)]
    for x, y in ((10, 10), (w - 10, 10), (10, 60), (w - 10, 60)):
        o.append(star(x, y, 2.2))
    o.append(heart(w / 2, 14, 6))
    return ''.join(o)


def cab_roof(w, h):
    o = []
    for x in range(4, int(w), 8):
        o.append('<rect x="%s" y="0" width="1.2" height="%s" fill="%s" opacity="0.5"/>' % (f(x), f(h), LOCO['cream']))
    return ''.join(o)


def boiler_decor(w, h):
    """w = Umfang, h = Laenge (y=0 vorne)."""
    o = []
    for y0, hh in ((4, 7), (60, 5), (h - 8, 8)):
        o.append('<rect x="0" y="%s" width="%s" height="%s" fill="%s"/>' % (f(y0), f(w), f(hh), LOCO['boilerd']))
        o.append('<rect x="0" y="%s" width="%s" height="1" fill="%s" opacity="0.7"/>' % (f(y0 + hh / 2 - 0.5), f(w), CREAM2))
    for i in range(40):
        x = (i * 37.3) % w
        y = 15 + (i * 23.7) % 40
        if abs(x - w / 2) > 14 and abs(x - w / 4) > 22 and abs(x - 3 * w / 4) > 22:
            o.append(star(x, y, 1.4, CREAM2))
    o.append('<circle cx="%s" cy="25" r="%s" fill="none" stroke="%s" stroke-width="0.5" stroke-dasharray="1.5,1.2"/>' % (
        f(w / 2), f(CHIM_R), WOODD))
    o.append(text(w / 2, 25 + 1.2, 'Schornstein', 3, WOODD))
    return ''.join(o)


def boiler_side(w, h):
    o = [tree(w * 0.55, h * 0.72 + 6, 26, TREE, TREED, snow=True),
         gift(w * 0.82, h * 0.72 + 6, 11, PINK),
         star(w * 0.25, h * 0.45, 3), star(w * 0.7, h * 0.18, 2.2), star(w * 0.88, h * 0.4, 1.8)]
    return ''.join(o)


def boiler_disc(w, h):
    cx, cy = w / 2, h / 2
    r = w / 2
    return ''.join([
        dot(cx, cy, r, LOCO['cream']),
        '<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="3"/>' % (f(cx), f(cy), f(r - 3), LOCO['boilerd']),
        dot(cx, cy, r * 0.45, LOCO['boiler']),
        star(cx, cy, r * 0.32, STAR),
        dot(cx, cy - r * 0.68, 4.5, STAR), dot(cx, cy - r * 0.68, 2.6, CREAM2)])


def chimney_decor(w, h):
    return ('<rect x="0" y="0" width="%s" height="7" fill="%s"/>'
            '<rect x="0" y="7" width="%s" height="1.2" fill="%s"/>' % (f(w), LOCO['d'], f(w), LOCO['cream'])) + \
        ''.join(star(x, 20, 1.8, CREAM2) for x in range(8, int(w), 16))


def cloud_decor(w, h):
    return ''.join([
        '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="#EFEDEA"/>' % (f(w * 0.55), f(h * 0.62), f(w * 0.3), f(h * 0.2)),
        dot(w * 0.38, h * 0.42, h * 0.16, WHITE), dot(w * 0.62, h * 0.38, h * 0.12, WHITE)])


# ---------------------------------------------------------------- Bastelteile
def point_in_poly(pt, poly):
    x, y = pt
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xi = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if xi > x:
                inside = not inside
    return inside


class Part:
    def __init__(self, name=''):
        self.name = name
        self.polys = []     # dict(pts, fill, decor, frame)
        self.circles = []   # dict(cx, cy, r, fill, decor)
        self.notes = []     # svg-Text, der mitgedruckt wird (nicht geschnitten)

    # orient: Richtung von "oben" des Dekors: 0=oben, 90=rechts, 180=unten, 270=links
    def rect(self, x, y, w, h, fill, decor=None, orient=0, tab=False):
        pts = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
        if orient == 0:
            fr = ((x, y), (1, 0), (0, 1), w, h)
        elif orient == 180:
            fr = ((x + w, y + h), (-1, 0), (0, -1), w, h)
        elif orient == 90:
            fr = ((x + w, y), (0, 1), (-1, 0), h, w)
        else:
            fr = ((x, y + h), (0, -1), (1, 0), h, w)
        self.polys.append(dict(pts=pts, fill=fill, decor=decor, frame=fr, tab=tab))
        return pts

    def poly(self, pts, fill=TAB, tab=True, label=True):
        self.polys.append(dict(pts=list(pts), fill=fill, decor=None, frame=None, tab=tab, label=label))

    def tab(self, a, b, depth, inset=None, label=True, **_):
        """Klebelasche an Kante a->b; zeigt automatisch von den Flaechen weg.
        inset=(am Punkt a, am Punkt b)."""
        ax, ay = a
        bx, by = b
        L = math.hypot(bx - ax, by - ay)
        ux, uy = (bx - ax) / L, (by - ay) / L
        nx, ny = uy, -ux
        mx, my = (ax + bx) / 2 + nx * 0.5, (ay + by) / 2 + ny * 0.5
        if any(not p['tab'] and point_in_poly((mx, my), p['pts']) for p in self.polys):
            nx, ny = -nx, -ny
        if inset is None:
            inset = min(depth * 0.6, L * 0.25)
        if isinstance(inset, tuple):
            i0, i1 = inset
        else:
            i0 = i1 = inset
        p = [a, b, (bx - ux * i1 + nx * depth, by - uy * i1 + ny * depth),
             (ax + ux * i0 + nx * depth, ay + uy * i0 + ny * depth)]
        self.poly(p, label=label)

    def circle(self, cx, cy, r, fill, decor=None):
        self.circles.append(dict(cx=cx, cy=cy, r=r, fill=fill, decor=decor))

    def note(self, s):
        self.notes.append(s)

    # ---- Kantenklassifikation
    def lines(self):
        polys = [p['pts'] for p in self.polys]
        edges = []
        for i, p in enumerate(polys):
            n = len(p)
            for k in range(n):
                edges.append((i, p[k], p[(k + 1) % n]))
        cuts, folds = [], []
        for (i, a, b) in edges:
            dx, dy = b[0] - a[0], b[1] - a[1]
            L2 = dx * dx + dy * dy
            if L2 < 1e-9:
                continue
            L = math.sqrt(L2)
            cov = []
            for (j, c, d) in edges:
                if j == i:
                    continue
                c1 = ((c[0] - a[0]) * dy - (c[1] - a[1]) * dx) / L
                c2 = ((d[0] - a[0]) * dy - (d[1] - a[1]) * dx) / L
                if abs(c1) > 1e-3 or abs(c2) > 1e-3:
                    continue
                t1 = ((c[0] - a[0]) * dx + (c[1] - a[1]) * dy) / L2
                t2 = ((d[0] - a[0]) * dx + (d[1] - a[1]) * dy) / L2
                lo, hi = max(0.0, min(t1, t2)), min(1.0, max(t1, t2))
                if hi - lo > 1e-6:
                    cov.append((lo, hi, j))
            cov.sort()
            t = 0.0
            pt = lambda s: (a[0] + dx * s, a[1] + dy * s)
            for lo, hi, j in cov:
                if lo > t + 1e-6:
                    cuts.append((pt(t), pt(lo)))
                if j > i and hi > max(lo, t) + 1e-6:
                    folds.append((pt(max(lo, t)), pt(hi)))
                t = max(t, hi)
            if t < 1 - 1e-6:
                cuts.append((pt(t), pt(1.0)))
        return cuts, folds

    # ---- SVG
    def svg_print(self):
        o = []
        for p in sorted(self.polys, key=lambda p: not p['tab']):
            ps = pts_str(p['pts'])
            if p['tab']:
                o.append('<polygon points="%s" fill="%s"/>' % (ps, p['fill']))
                if p.get('label', True):
                    xs = [q[0] for q in p['pts']]
                    ys = [q[1] for q in p['pts']]
                    w, h = max(xs) - min(xs), max(ys) - min(ys)
                    if max(w, h) > 14 and min(w, h) > 4.5:
                        rot = 90 if h > w else 0
                        cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
                        o.append('<text x="%s" y="%s" font-family="%s" font-size="2.6" fill="#A39686" text-anchor="middle" transform="rotate(%s %s %s)">kleben</text>' % (
                            f(cx), f(cy + 0.9), FONT_TXT, rot, f(cx), f(cy)))
            else:
                o.append('<polygon points="%s" fill="%s" stroke="%s" stroke-width="0.8" stroke-linejoin="round"/>' % (ps, p['fill'], p['fill']))
        for p in self.polys:
            if p['decor'] and p['frame']:
                (x0, y0), u, dd, w, h = p['frame']
                cid = clip_uid()
                o.append('<g transform="matrix(%s,%s,%s,%s,%s,%s)"><clipPath id="%s"><rect x="-0.3" y="-0.3" width="%s" height="%s"/></clipPath><g clip-path="url(#%s)">%s</g></g>' % (
                    f(u[0]), f(u[1]), f(dd[0]), f(dd[1]), f(x0), f(y0), cid, f(w + 0.6), f(h + 0.6), cid, p['decor'](w, h)))
        for c in self.circles:
            o.append('<circle cx="%s" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="0.8"/>' % (
                f(c['cx']), f(c['cy']), f(c['r']), c['fill'], c['fill']))
            if c['decor']:
                o.append('<g transform="translate(%s,%s)">%s</g>' % (f(c['cx'] - c['r']), f(c['cy'] - c['r']), c['decor'](2 * c['r'], 2 * c['r'])))
        o.extend(self.notes)
        return ''.join(o)

    def svg_cut(self, color=CUT, width=0.3):
        cuts, _ = self.lines()
        o = ['<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round"/>' % (
            ' '.join('M%s,%s L%s,%s' % (f(a[0]), f(a[1]), f(b[0]), f(b[1])) for a, b in cuts), color, width)]
        for c in self.circles:
            o.append('<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="%s"/>' % (
                f(c['cx']), f(c['cy']), f(c['r']), color, width))
        return ''.join(o)

    def svg_fold(self, color=FOLD, width=0.3, dash='2.2,1.4'):
        _, folds = self.lines()
        if not folds:
            return ''
        return '<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-dasharray="%s"/>' % (
            ' '.join('M%s,%s L%s,%s' % (f(a[0]), f(a[1]), f(b[0]), f(b[1])) for a, b in folds), color, width, dash)

    def bbox(self):
        xs, ys = [], []
        for p in self.polys:
            xs += [q[0] for q in p['pts']]
            ys += [q[1] for q in p['pts']]
        for c in self.circles:
            xs += [c['cx'] - c['r'], c['cx'] + c['r']]
            ys += [c['cy'] - c['r'], c['cy'] + c['r']]
        return min(xs), min(ys), max(xs), max(ys)


# ---------------------------------------------------------------- Konkrete Teile
def part_box_bottom(W, ox, oy, rotated=False):
    """Kaestchen-Unterteil als L-Netz. rotated=True -> um 180 Grad gedreht."""
    P = Part('Kästchen-Unterteil')
    s, t = BOX, BOX_TAB
    deco, base = box_wall(W)
    total_h = 4 * s

    def X(x, y):
        if rotated:
            return (ox - x, oy + total_h - y)
        return (ox + x, oy + y)

    for k in range(4):
        a = X(0, k * s)
        b = X(s, (k + 1) * s)
        x0, y0 = min(a[0], b[0]), min(a[1], b[1])
        P.rect(x0, y0, s, s, base, deco, orient=90 if rotated else 270)
    a, b = X(s, 3 * s), X(2 * s, 4 * s)
    P.rect(min(a[0], b[0]), min(a[1], b[1]), s, s, mix(W['c'], WHITE, 0.6), plain_label(['Boden']), orient=0)
    # Klebelasche Ring-Schluss
    side = 1
    P.tab(X(s, 0), X(0, 0), t, inset=2.5, side=side)
    # Bodenlaschen
    for k in range(3):
        P.tab(X(s, (k + 1) * s), X(s, k * s), t, inset=(2.5, 2.5), side=side)
    return P


def part_lid(W, num, ox, oy):
    P = Part('Deckel %d' % num)
    s, h = LID, LID_H
    x0, y0 = ox + h, oy + h
    P.rect(x0, y0, s, s, mix(W['c'], WHITE, 0.25), lid_top(W, num))
    wall = lid_wall(W, num)
    P.rect(x0, oy, s, h, W['c'], wall, orient=180)
    P.rect(x0, y0 + s, s, h, W['c'], wall, orient=0)
    P.rect(ox, y0, h, s, W['c'], wall, orient=90)
    P.rect(x0 + s, y0, h, s, W['c'], wall, orient=270)
    # Laschen an Ober- und Unterkante, greifen in die Ecken
    for a, b in (((x0, y0), (x0, oy)), ((x0 + s, oy), (x0 + s, y0)),
                 ((x0, y0 + s + h), (x0, y0 + s)), ((x0 + s, y0 + s), (x0 + s, y0 + s + h))):
        P.tab(a, b, h * 0.85, inset=2)
    return P


def part_wagon_a(W, ox, oy):
    P = Part('Waggon %d Teil A' % W['n'])
    e, s, H = WG_LOW, WG, WG_H
    fx, fy = ox + e, oy + H
    P.rect(fx, fy, s, s, mix(W['c'], WHITE, 0.55),
           plain_label(['Waggon %d · Teil A' % W['n'], 'Unterseite – wird nicht gesehen',
                        'Wände nach oben falten,', 'bedruckte Seite nach außen'], size=4.2))
    side = wagon_side(W)
    P.rect(fx, oy, s, H, W['c'], side, orient=0)
    P.rect(fx, fy + s, s, H, W['c'], side, orient=180)
    endf = wagon_endflap(W)
    P.rect(ox, fy, e, s, W['c'], endf, orient=270)
    P.rect(fx + s, fy, e, s, W['c'], endf, orient=90)
    # Laschen an den Seitenwaenden (aussen links/rechts)
    P.tab((fx, fy), (fx, oy), 10, inset=(5, 2.5), side=1)
    P.tab((fx + s, oy), (fx + s, fy), 10, inset=(2.5, 5), side=1)
    P.tab((fx, fy + s + H), (fx, fy + s), 10, inset=(2.5, 5), side=1)
    P.tab((fx + s, fy + s), (fx + s, fy + s + H), 10, inset=(5, 2.5), side=1)
    return P


def part_wagon_b(W, ox, oy):
    P = Part('Waggon %d Teil B' % W['n'])
    e, s, H = WG_LOW, WG_B, WG_H - WG_LOW
    fx, fy = ox + e, oy + H
    P.rect(fx, fy, s, s, CREAM2,
           plain_label(['Waggon %d · Teil B' % W['n'], 'Zwischenboden (Unterseite)',
                        'Stirnwände nach oben,', 'Stützen nach unten falten'], size=4.2))
    endw = wagon_endwall(W)
    P.rect(fx, oy, s, H, W['c'], endw, orient=0)
    P.rect(fx, fy + s, s, H, W['c'], endw, orient=180)
    leg = plain_label(['Stütze'], size=3.6, opacity=0.5)
    P.rect(ox, fy, e, s, CREAM2, leg, orient=90)
    P.rect(fx + s, fy, e, s, CREAM2, leg, orient=270)
    return P


def part_chassis(ox, oy):
    P = Part('Lok Fahrgestell')
    L, Wd, H = CH_L, CH_W, CH_H
    tx, ty = ox + H, oy + H
    P.rect(tx, ty, L, Wd, LOCO['d'], chassis_top)
    P.rect(tx, oy, L, H, LOCO['c'], chassis_side(True), orient=180)
    P.rect(tx, ty + Wd, L, H, LOCO['c'], chassis_side(False), orient=0)
    P.rect(ox, ty, H, Wd, LOCO['c'], chassis_front, orient=90)
    P.rect(tx + L, ty, H, Wd, LOCO['c'], chassis_back, orient=270)
    for a, b in (((tx, ty), (tx, oy)), ((tx + L, oy), (tx + L, ty)),
                 ((tx, ty + Wd + H), (tx, ty + Wd)), ((tx + L, ty + Wd), (tx + L, ty + Wd + H))):
        P.tab(a, b, 10, inset=3)
    return P


def part_cab(ox, oy):
    P = Part('Lok Führerhaus')
    a, b, h = CAB_A, CAB_B, CAB_H
    y0 = oy + CAB_ROOF
    xs = [ox, ox + a, ox + a + b, ox + 2 * a + b, ox + 2 * a + 2 * b]
    P.rect(xs[0], y0, a, h, LOCO['cream'], cab_side)
    P.rect(xs[1], y0, b, h, LOCO['cream'], cab_front)
    P.rect(xs[2], y0, a, h, LOCO['cream'], cab_side)
    P.rect(xs[3], y0, b, h, LOCO['cream'], cab_back)
    P.rect(xs[1], oy, b, CAB_ROOF, LOCO['d'], cab_roof)
    # Schlusslasche
    P.tab((xs[4], y0), (xs[4], y0 + h), 10, inset=3, side=1)
    # Dachlaschen (Seiten + Rueckwand)
    for i in (0, 2, 3):
        P.tab((xs[i], y0), (xs[i + 1], y0), 9, inset=3, side=1)
    # Bodenlaschen
    for i in range(4):
        P.tab((xs[i + 1], y0 + h), (xs[i], y0 + h), 9, inset=3, side=1)
    return P


def part_boiler(ox, oy):
    P = Part('Lok Kessel')
    C = 2 * math.pi * BOILER_R
    L = BOILER_L
    P.rect(ox, oy, C, L, LOCO['boiler'], boiler_decor)
    # Seitendekor (zwei Seiten) als zusaetzliche "Fenster" ohne eigene Kanten -> per note
    for cx, orient in ((C / 4, 90), (3 * C / 4, 270)):
        w, h = 60, 80
        x0, y0 = ox + cx - w / 2, oy + 15
        if orient == 90:
            fr = ((x0 + w, y0), (0, 1), (-1, 0), h, w)
        else:
            fr = ((x0, y0 + h), (0, -1), (1, 0), h, w)
        (px, py), u, dd, lw, lh = fr
        P.note('<g transform="matrix(%s,%s,%s,%s,%s,%s)">%s</g>' % (
            f(u[0]), f(u[1]), f(dd[0]), f(dd[1]), f(px), f(py), boiler_side(lw, lh)))
    P.tab((ox + C, oy + L), (ox + C, oy), 10, inset=3, side=1)
    n = 16
    for k in range(n):
        x0 = ox + C * k / n
        x1 = ox + C * (k + 1) / n
        P.tab((x0, oy), (x1, oy), 8, inset=2.2, side=1, label=False)
        P.tab((x1, oy + L), (x0, oy + L), 8, inset=2.2, side=1, label=False)
    return P


def part_disc(cx, cy):
    P = Part('Kessel-Deckel')
    P.circle(cx, cy, BOILER_R + 0.5, LOCO['cream'], boiler_disc)
    return P


def chimney_profile(n=48):
    r, R = CHIM_R, BOILER_R
    C = 2 * math.pi * r
    pts = []
    for i in range(n + 1):
        th = 2 * math.pi * i / n
        hgt = CHIM_H + math.sqrt(R * R - r * r) - math.sqrt(R * R - (r * math.sin(th)) ** 2)
        pts.append((C * i / n, hgt))
    return C, pts


def part_chimney(ox, oy):
    P = Part('Schornstein')
    C, prof = chimney_profile()
    body = [(ox, oy), (ox + C, oy)] + [(ox + x, oy + y) for x, y in reversed(prof)]
    P.polys.append(dict(pts=body, fill=LOCO['c'], decor=chimney_decor,
                        frame=((ox, oy), (1, 0), (0, 1), C, CHIM_H + 3), tab=False))
    P.tab((ox + C, oy + prof[-1][1]), (ox + C, oy), 7, inset=2, side=1)
    m = 6
    for k in range(0, len(prof) - 1, m):
        seg = [(ox + x, oy + y) for x, y in prof[k:k + m + 1]]
        a, b = seg[0], seg[-1]
        outer = [(b[0] - 1.6, b[1] + 7), (a[0] + 1.6, a[1] + 7)]
        P.poly(seg + outer, label=False)
    return P


def cloud_shape(cx, cy, scale=1.0):
    circles = [(0, 0, 14), (15, -6, 12), (-15, -3, 11), (27, 3, 9), (-26, 6, 8), (6, 8, 12), (-8, 8, 10), (18, 8, 9)]
    pts = []
    for i in range(240):
        a = 2 * math.pi * i / 240
        dx, dy = math.cos(a), math.sin(a)
        best = 0
        for (x, y, r) in circles:
            b = x * dx + y * dy
            c = x * x + y * y - r * r
            disc = b * b - c
            if disc >= 0:
                best = max(best, b + math.sqrt(disc))
        pts.append((cx + best * dx * scale, cy + best * dy * scale))
    return pts


def part_cloud(cx, cy):
    P = Part('Rauchwolke')
    pts = cloud_shape(cx, cy, 1.15)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    P.polys.append(dict(pts=pts, fill=WHITE, decor=cloud_decor,
                        frame=((min(xs), min(ys)), (1, 0), (0, 1), max(xs) - min(xs), max(ys) - min(ys)), tab=False))
    return P


def part_wheel(cx, cy, r, col=WOOD):
    P = Part('Rad')
    P.circle(cx, cy, r, col, wheel_decor(r, col))
    return P


def part_hub(cx, cy, r):
    P = Part('Radkappe')
    P.circle(cx, cy, r, CREAM, hub_decor(r))
    return P


def part_coupling(x, y, w=60, h=16):
    P = Part('Kupplung')
    P.rect(x, y, w, h / 2, WOODD)
    P.rect(x, y + h / 2, w, h / 2, WOODD)
    return P


def part_rod(x, y, w=100, h=6):
    P = Part('Treibstange')
    P.rect(x, y, w, h, WOOD2, lambda ww, hh: dot(4, hh / 2, 1.5, CREAM) + dot(ww - 4, hh / 2, 1.5, CREAM))
    return P
