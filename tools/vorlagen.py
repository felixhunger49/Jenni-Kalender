"""Seitenlayout der Druckvorlagen (A4) und Export als SVG."""
from zug import *

PORTRAIT = (210.0, 297.0)
LANDSCAPE = (297.0, 210.0)


class Page:
    def __init__(self, key, title, hint, size=PORTRAIT, header=True, copies=1):
        self.key = key
        self.title = title
        self.hint = hint
        self.size = size
        self.header = header
        self.copies = copies
        self.parts = []
        self.extra = []

    def add(self, part):
        self.parts.append(part)
        return part

    # Kopfzeile, Legende, Massstab
    def chrome(self, legend_at=None, scale_at=None, title_at=None, vertical=False):
        W, H = self.size
        o = []
        if self.header:
            o.append(text(10, 13, self.title, 8.5, INK, anchor='start', font=FONT_HAND))
            o.append(text(10, 19.5, self.hint, 3.4, mix(INK, '#FFFFFF', 0.25), anchor='start'))
            lx, ly = W - 10, 10
            o.append(self._legend(lx, ly, 'end'))
        if legend_at:
            o.append(self._legend(legend_at[0], legend_at[1], 'start', vertical))
        if title_at:
            x, y, rot = title_at
            o.append('<g transform="translate(%s,%s) rotate(%s)">%s%s</g>' % (
                f(x), f(y), f(rot), text(0, 0, self.title, 7, INK, anchor='start', font=FONT_HAND),
                text(0, 5.5, self.hint, 3, mix(INK, '#FFFFFF', 0.25), anchor='start')))
        sx, sy = scale_at or ((W - 128, 17.5) if W > H else (10, H - 9))
        if vertical and scale_at:
            o.append('<g transform="translate(%s,%s) rotate(-90)">%s</g>' % (f(sx), f(sy), self._scale(0, 0, True)))
        else:
            o.append(self._scale(sx, sy))
        if self.copies > 1:
            o.append(text(W - 10, H - 7, '%d× drucken' % self.copies, 4.2, '#B0574A', anchor='end', weight='bold'))
        return ''.join(o)

    def _scale(self, x, y, short=False):
        lab = '5 cm' if short else '5 cm – bitte nachmessen (100 % drucken)'
        return ''.join([
            '<rect x="%s" y="%s" width="50" height="2" fill="%s"/>' % (f(x), f(y), INK),
            '<rect x="%s" y="%s" width="10" height="2" fill="#FFFFFF"/>' % (f(x + 10), f(y)),
            '<rect x="%s" y="%s" width="10" height="2" fill="#FFFFFF"/>' % (f(x + 30), f(y)),
            '<rect x="%s" y="%s" width="50" height="2" fill="none" stroke="%s" stroke-width="0.25"/>' % (f(x), f(y), INK),
            text(x + 52, y + 1.9, lab, 2.8, INK, anchor='start')])

    def _legend(self, x, y, anchor, vertical=False):
        items = [('cut', 'schneiden'), ('fold', 'falzen'), ('tab', 'Klebelasche')]
        o = []
        if vertical:
            for i, (k, lab) in enumerate(items):
                o.append(self._legend_item(x, y + i * 6, k, lab))
            return ''.join(o)
        widths = [24, 20, 26]
        total = sum(widths)
        cx = x - total if anchor == 'end' else x
        for (k, lab), w in zip(items, widths):
            o.append(self._legend_item(cx, y, k, lab))
            cx += w
        return ''.join(o)

    def _legend_item(self, x, y, kind, label):
        if kind == 'cut':
            g = '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.35"/>' % (f(x), f(y), f(x + 7), f(y), CUT)
        elif kind == 'fold':
            g = '<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="0.35" stroke-dasharray="2.2,1.4"/>' % (f(x), f(y), f(x + 7), f(y), FOLD)
        else:
            g = '<rect x="%s" y="%s" width="7" height="3.2" fill="%s"/>' % (f(x), f(y - 1.6), TAB)
        return g + text(x + 8.5, y + 1.1, label, 3, INK, anchor='start')

    def svg(self, mode='print', chrome=''):
        """mode: print (Druck + Linien), plot (nur Schnitt/Falz fuer Plotter)."""
        W, H = self.size
        o = ['<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
             'width="%smm" height="%smm" viewBox="0 0 %s %s">' % (f(W), f(H), f(W), f(H))]
        if mode == 'print':
            o.append('<g id="druck" inkscape:groupmode="layer" inkscape:label="Druck">')
            o.append('<rect width="%s" height="%s" fill="#FFFFFF"/>' % (f(W), f(H)))
            for p in self.parts:
                o.append(p.svg_print())
            o.extend(self.extra)
            o.append(chrome)
            o.append('</g>')
        o.append('<g id="falzen" inkscape:groupmode="layer" inkscape:label="Falzen (rillen)">')
        for p in self.parts:
            o.append(p.svg_fold(FOLD if mode == 'print' else '#0000FF'))
        o.append('</g>')
        o.append('<g id="schneiden" inkscape:groupmode="layer" inkscape:label="Schneiden">')
        for p in self.parts:
            o.append(p.svg_cut(CUT if mode == 'print' else '#FF0000'))
        o.append('</g></svg>')
        return '\n'.join(o)


def label(x, y, s, size=3.4, anchor='middle', col=INK):
    return text(x, y, s, size, col, anchor=anchor)


def build_pages():
    pages = []

    # ---------------- Lok
    p = Page('lok-1-fahrgestell', 'Lok · Fahrgestell', 'Falzlinien rillen, Wände nach unten falten, Laschen innen festkleben.', LANDSCAPE)
    P = p.add(part_chassis(28, 38))
    p._chrome = dict()
    pages.append(p)

    p = Page('lok-2-fuehrerhaus', 'Lok · Führerhaus', 'Wände zum Häuschen falten, Dach schließen, Bodenlaschen nach innen.', LANDSCAPE)
    p.add(part_cab(8.5, 28))
    pages.append(p)

    p = Page('lok-3-kessel', 'Lok · Kessel, Deckel, Schornstein, Rauchwolke', 'Kessel zur Röhre rollen (Naht unten). Zacken vorne nach innen, hinten nach außen.', LANDSCAPE)
    p.add(part_boiler(10, 30))
    p.add(part_disc(260, 72))
    p.add(part_chimney(14, 156))
    p.add(part_cloud(150, 182))
    p.extra.append(label(260, 112, 'Kessel-Deckel (vorne)'))
    p.extra.append(label(55, 153, 'Schornstein'))
    p.extra.append(label(150, 160, 'Rauchwolke (optional)'))
    pages.append(p)

    # ---------------- Raeder
    p = Page('raeder-1', 'Räder (1/2)', '16 Waggon-Räder und 4 Lok-Räder. Tipp: auf Graupappe kleben, dann ausschneiden – so werden sie stabiler.')
    for i in range(16):
        cx = 22 + 44 * (i % 4) + 4
        cy = 48 + 44 * (i // 4)
        p.add(part_wheel(cx, cy, WG_WHEEL_R))
    for cx, r in ((40, LOCO_REAR_R), (96, LOCO_REAR_R), (142, LOCO_FRONT_R), (182, LOCO_FRONT_R)):
        p.add(part_wheel(cx, 255, r))
    p.extra.append(label(68, 284, '2× Lok hinten (groß)'))
    p.extra.append(label(162, 284, '2× Lok vorne (klein)'))
    pages.append(p)

    p = Page('raeder-2', 'Räder (2/2), Radkappen, Kupplungen', '8 Waggon-Räder. Radkappen und Treibstangen sind optional (für mehr 3D-Effekt).')
    for i in range(8):
        cx = 26 + 44 * (i % 4)
        cy = 48 + 44 * (i // 4)
        p.add(part_wheel(cx, cy, WG_WHEEL_R))
    for i in range(28):
        cx = 18 + 17.5 * (i % 10)
        cy = 128 + 17.5 * (i // 10)
        p.add(part_hub(cx, cy, 7))
    p.extra.append(label(105, 120, 'Radkappen (optional, 28 Stück)'))
    for i in range(6):
        p.add(part_coupling(14 + 64 * (i % 3), 196 + 26 * (i // 3)))
    p.extra.append(label(105, 190, 'Kupplungen – längs falten und zwischen die Waggons kleben (6 Stück)'))
    for i in range(2):
        p.add(part_rod(12 + 96 * i, 262, w=94))
    p.extra.append(label(105, 255, 'Treibstangen für die Lok (optional)'))
    pages.append(p)

    # ---------------- Waggons
    for W in WAGONS:
        n = W['n']
        p = Page('waggon-%d-a' % n, 'Waggon %d (%s) · Teil A' % (n, W['name']),
                 'Seitenwände + Boden', header=False)
        p.add(part_wagon_a(W, 10, 8.5))
        p._special = 'wagon_a'
        pages.append(p)

        p = Page('waggon-%d-b' % n, 'Waggon %d (%s) · Teil B' % (n, W['name']),
                 'Zwischenboden mit Stirnwänden. Stirnwände nach oben, Stützen nach unten falten.')
        p.add(part_wagon_b(W, 10, 52))
        pages.append(p)

        nums = list(range(4 * n - 3, 4 * n + 1))
        p = Page('waggon-%d-kaestchen' % n, 'Kästchen %d–%d · Unterteile' % (nums[0], nums[-1]),
                 'Zwei Unterteile pro Blatt – für Waggon %d dieses Blatt 2× drucken.' % n, copies=2)
        p.add(part_box_bottom(W, 17.5, 42))
        p.add(part_box_bottom(W, 17.5 + 175, 42, rotated=True))
        pages.append(p)

        p = Page('waggon-%d-deckel' % n, 'Kästchen %d–%d · Deckel' % (nums[0], nums[-1]),
                 'Ränder nach unten falten, Eck-Laschen innen festkleben.')
        for i, num in enumerate(nums):
            p.add(part_lid(W, num, 8 + 100 * (i % 2), 48 + 100 * (i // 2)))
        pages.append(p)
    return pages


def page_chrome(p):
    W, H = p.size
    if getattr(p, '_special', None) == 'wagon_a':
        return p.chrome(legend_at=(176, 14), scale_at=(18, 285), vertical=True,
                        title_at=None) + \
            '<g transform="translate(13,14)">%s%s</g>' % (
                text(0, 0, p.title.split(' · ')[0], 4.6, INK, anchor='start', font=FONT_HAND),
                text(0, 5, 'Teil A', 4.6, INK, anchor='start', font=FONT_HAND))
    return p.chrome()


def check_pages(pages):
    """Prueft, ob alle Teile innerhalb der Seite (mit Rand) liegen."""
    problems = []
    for p in pages:
        W, H = p.size
        for part in p.parts:
            x0, y0, x1, y1 = part.bbox()
            if x0 < 4 or y0 < 4 or x1 > W - 4 or y1 > H - 4:
                problems.append('%s: %s ragt aus der Seite (%.1f,%.1f,%.1f,%.1f)' % (p.key, part.name, x0, y0, x1, y1))
    return problems
