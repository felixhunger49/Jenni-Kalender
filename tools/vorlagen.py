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
    def chrome(self, legend_at=None, scale_at=None, title_at=None, vertical=False, short=False):
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
            o.append(self._scale(sx, sy, short))
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

    # ---------------- Kleinteile
    p = Page('kleinteile', 'Kupplungen und Treibstangen', 'Die Räder sind schon an Waggons und Lok angesetzt. Hier nur noch die Kleinteile (optional).')
    for i in range(4):
        p.add(part_coupling(14 + 64 * (i % 3), 56 + 26 * (i // 3)))
    p.extra.append(label(105, 48, 'Kupplungen – längs falten und zwischen die Waggons kleben (4 Stück)'))
    for i in range(2):
        p.add(part_rod(12 + 96 * i, 128, w=94))
    p.extra.append(label(105, 121, 'Treibstangen für die Lok – von Rad zu Rad kleben'))
    pages.append(p)

    # ---------------- Waggons
    for W in WAGONS:
        n = W['n']
        p = Page('waggon-%d-a' % n, 'Waggon %d (%s) · Teil A' % (n, W['name']),
                 'Boden, Stirnwände und eine lange Wand. Räder mit ausschneiden.', LANDSCAPE)
        p.add(part_wagon_a(W, 8.5, 22))
        p._special = 'wagon_a'
        pages.append(p)
    for n0 in (1, 3):
        p = Page('waggon-%d%d-b' % (n0, n0 + 1), 'Waggon %d + %d · Teil B' % (n0, n0 + 1),
                 'Die zweite lange Seitenwand je Waggon. Räder mit ausschneiden, Bodenlaschen nach innen.')
        for k, W in enumerate(WAGONS[n0 - 1:n0 + 1]):
            oy = 40 + 125 * k
            p.add(part_wagon_b(W, 45, oy))
            p.extra.append(label(105, oy - 6, 'Waggon %d (%s)' % (W['n'], W['name']), 4.4))
        pages.append(p)
    for W in WAGONS:
        for num in range(6 * W['n'] - 5, 6 * W['n'] + 1):
            p = Page('kaestchen-%02d' % num, 'Kästchen %d · Waggon %d' % (num, W['n']),
                     'Ein Teil mit Klappdeckel: Wände zum Ring kleben, Boden einkleben, Deckel mit Zunge schließen.')
            p.add(part_box(W, num, 22, 40))
            pages.append(p)
    return pages


def page_chrome(p):
    W, H = p.size
    if getattr(p, '_special', None) == 'wagon_a':
        return p.chrome(scale_at=(225, 50), short=True)
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
