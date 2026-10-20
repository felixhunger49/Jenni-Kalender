"""Bebilderte Schritt-fuer-Schritt-Anleitung (HTML -> PDF)."""
from zug import (text, INK, CUT, FOLD, TAB, WAGONS, part_box_bottom, part_lid, part_wagon_a, part_wagon_b,
                 part_chassis, part_cab, part_boiler, part_disc, part_chimney, part_cloud, part_wheel, f, mix)
from iso import render, Cam
import modelle as M

CSS = '''
body { font-family: 'Nunito', sans-serif; color: #5A4636; }
.page.doc { background: #FBF7F1; padding: 12mm 14mm 12mm; box-sizing: border-box; }
h1, h2, h3, .hand { font-family: 'Patrick Hand', cursive; font-weight: normal; }
h1 { font-size: 30pt; margin: 0; line-height: 1.05; }
h2 { font-size: 21pt; margin: 0 0 1mm; }
h3 { font-size: 13.5pt; margin: 0 0 0.6mm; }
p, li, td { font-size: 9.6pt; line-height: 1.38; }
p { margin: 0 0 2mm; }
.sub { font-size: 11pt; letter-spacing: 0.08em; text-transform: uppercase; color: #8C7A68; margin-top: 2mm; }
.lead { font-size: 10.5pt; color: #7A6656; margin-bottom: 4mm; }
.cover-fig { height: 92mm; margin: 6mm -8mm 2mm; }
.cover-fig svg, .fig svg, .thumb svg { width: 100%; height: 100%; display: block; }
.chips { display: flex; gap: 3mm; justify-content: center; margin: 3mm 0 5mm; }
.chip { background: #EFE5D6; border-radius: 20mm; padding: 1.6mm 5mm; font-size: 10pt; }
.cols { display: grid; grid-template-columns: 1fr 1fr; gap: 5mm 7mm; }
.box { background: #FFFFFF; border: 0.3mm solid #E8DDCD; border-radius: 3mm; padding: 4mm 5mm; }
.box ul { margin: 0; padding-left: 4.5mm; }
.box li { margin-bottom: 0.8mm; }
table { border-collapse: collapse; width: 100%; }
td, th { padding: 0.62mm 1.5mm; text-align: left; border-bottom: 0.2mm solid #EDE3D5; font-size: 9pt; }
th { font-size: 8.4pt; text-transform: uppercase; letter-spacing: 0.06em; color: #8C7A68; font-weight: 600; }
td.n { text-align: center; width: 9mm; }
td.k { text-align: center; width: 14mm; font-weight: 700; }
.steps { display: grid; grid-template-columns: 1fr 1fr; gap: 3.5mm 6mm; }
.step { background: #FFFFFF; border: 0.3mm solid #E8DDCD; border-radius: 3mm; padding: 3mm 4mm 3.2mm; position: relative; }
.step .fig { height: 45mm; margin-bottom: 2mm; }
.step .num { position: absolute; top: 2.5mm; left: 3mm; width: 8mm; height: 8mm; border-radius: 50%; background: #C98E6E;
             color: #fff; font-family: 'Patrick Hand', cursive; font-size: 15pt; line-height: 8.3mm; text-align: center; }
.step p { font-size: 9.1pt; margin: 0; }
.head { display: flex; align-items: baseline; gap: 5mm; margin-bottom: 4mm; border-bottom: 0.4mm dashed #D9C9B4; padding-bottom: 2.5mm; }
.head .tag { font-family: 'Patrick Hand', cursive; font-size: 13pt; color: #C98E6E; }
.legend { display: flex; flex-direction: column; gap: 1.6mm; }
.legend div { display: flex; align-items: center; gap: 3mm; font-size: 9.4pt; }
.tip { background: #F3EADB; border-radius: 3mm; padding: 3mm 4.5mm; margin-top: 4mm; font-size: 9.4pt; }
.foot { position: absolute; bottom: 6mm; left: 0; right: 0; text-align: center; font-size: 8pt; color: #A39686; }
.thumbs { display: flex; gap: 3mm; height: 45mm; align-items: center; justify-content: center; }
.thumb { height: 100%; flex: 1; }
.wide { grid-column: 1 / span 2; }
.wide .fig { height: 62mm; }
'''


def page_footer(p, i, n):
    W, H = p.size
    return text(W / 2, H - 4, 'Eisenbahn-Adventskalender · Vorlage %d/%d' % (i, n), 2.8, '#A39686')


def thumb(parts, pad=3):
    xs0, ys0, xs1, ys1 = [], [], [], []
    for p in parts:
        a, b, c, d = p.bbox()
        xs0.append(a); ys0.append(b); xs1.append(c); ys1.append(d)
    x0, y0, x1, y1 = min(xs0) - pad, min(ys0) - pad, max(xs1) + pad, max(ys1) + pad
    inner = ''.join(p.svg_print() + p.svg_fold(FOLD, 0.6, '3,2') + p.svg_cut(CUT, 0.6) for p in parts)
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s %s %s %s" preserveAspectRatio="xMidYMid meet">%s</svg>' % (
        f(x0), f(y0), f(x1 - x0), f(y1 - y0), inner)


def step(n, title, txt, fig_html, wide=False):
    return '<div class="step%s"><div class="num">%d</div><div class="fig">%s</div><h3>%s</h3><p>%s</p></div>' % (
        ' wide' if wide else '', n, fig_html, title, txt)


def doc_page(inner, num):
    return '<div class="page doc">%s<div class="foot">Eisenbahn-Adventskalender · Anleitung · Seite %d</div></div>' % (inner, num)


def body(pages):
    W1 = WAGONS[0]
    W2 = WAGONS[1]
    out = []
    pg = [0]

    def add(inner):
        pg[0] += 1
        out.append(doc_page(inner, pg[0]))

    # ------------------------------------------------ Titelseite
    cover = render(M.train_model(), Cam(yaw=16, pitch=20), pad=10)
    add('''
<div style="text-align:center; margin-top:4mm">
  <h1 style="font-size:40pt">Eisenbahn-Adventskalender</h1>
  <div class="sub">Bastelvorlage &amp; Schritt-für-Schritt-Anleitung</div>
</div>
<div class="cover-fig">%s</div>
<div class="chips"><span class="chip">24 Kästchen</span><span class="chip">6 Waggons</span><span class="chip">1 Lok</span></div>
<div class="cols">
 <div class="box"><h3>So ist der Zug gebaut</h3>
  <p>Jedes Teil ist möglichst <b>aus einem Stück gefaltet</b> und nur an Laschen geklebt. Die Räder werden zum Schluss aufgeklebt.</p>
  <ul>
   <li><b>Lok:</b> Fahrgestell, Führerhaus, Kessel (+ Deckel) und Schornstein</li>
   <li><b>Waggon:</b> nur 2 Teile – Teil A (Boden + Wände) und Teil B (Zwischenboden mit Stirnwänden), oben offen</li>
   <li><b>Kästchen:</b> Unterteil + Deckel mit Zahl, 4 Stück pro Waggon</li>
  </ul></div>
 <div class="box"><h3>Größen (fertig)</h3>
  <table>
   <tr><td>Kästchen</td><td>5,5 × 5,5 × 5,5 cm innen</td></tr>
   <tr><td>Waggon</td><td>12 × 12 cm, 8,8 cm hoch (mit Rädern)</td></tr>
   <tr><td>Lok</td><td>19 × 9 cm, ca. 18 cm hoch mit Rauch</td></tr>
   <tr><td>ganzer Zug</td><td>ca. 1 m lang</td></tr>
  </table>
  <p style="margin-top:2mm">Die Kästchen stehen im Waggon auf einem Zwischenboden und schauen oben gut 1 cm heraus – so lassen sie sich leicht herausnehmen.</p></div>
 <div class="box wide"><h3>Was du bekommst</h3>
  <table>
   <tr><td><b>Vorlagen (PDF)</b></td><td>29 farbige Druckvorlagen in Originalgröße: Lok, Räder, 6 Waggons, 24 Kästchen mit Zahlen 1–24</td></tr>
   <tr><td><b>Anleitung (PDF)</b></td><td>dieses Heft mit Material, Drucktipps und bebilderten Bauschritten</td></tr>
   <tr><td><b>SVG – Druck</b></td><td>jede Vorlage einzeln, mit Ebenen „Druck“, „Schneiden“, „Falzen“</td></tr>
   <tr><td><b>SVG – Plotter</b></td><td>nur Schnitt- (rot) und Rilllinien (blau) für Cricut, Silhouette &amp; Co.</td></tr>
  </table></div>
</div>
''' % cover)

    # ------------------------------------------------ Uebersicht
    rows = []
    for i, p in enumerate(pages, 1):
        rows.append('<tr><td class="n">%d</td><td>%s</td><td class="k">%s</td></tr>' % (
            i, p.title, '%d×' % p.copies))
    half = (len(rows) + 1) // 2
    tbl = lambda r: '<table><tr><th>Blatt</th><th>Inhalt</th><th>drucken</th></tr>%s</table>' % ''.join(r)
    legend_svg = lambda kind: {
        'cut': '<svg width="14mm" height="4mm" viewBox="0 0 14 4"><line x1="0" y1="2" x2="14" y2="2" stroke="%s" stroke-width="0.4"/></svg>' % CUT,
        'fold': '<svg width="14mm" height="4mm" viewBox="0 0 14 4"><line x1="0" y1="2" x2="14" y2="2" stroke="%s" stroke-width="0.4" stroke-dasharray="2.2,1.4"/></svg>' % FOLD,
        'tab': '<svg width="14mm" height="4mm" viewBox="0 0 14 4"><polygon points="0,4 2,0 12,0 14,4" fill="%s"/></svg>' % TAB,
        'wheel': '<svg width="14mm" height="6mm" viewBox="0 0 14 6"><circle cx="7" cy="3" r="2.7" fill="none" stroke="#6E523C" stroke-width="0.3" stroke-dasharray="0.8,0.8"/></svg>',
    }[kind]
    add('''
<div class="head"><h2>Bevor es losgeht</h2><span class="tag">Material, Drucken, Grundtechnik</span></div>
<div class="cols">
 <div class="box"><h3>Das brauchst du</h3><ul>
  <li>Druckerpapier-Karton <b>250–300 g/m²</b>, weiß (ca. 35 Blatt A4 – siehe Tabelle)</li>
  <li>Schere, für Innenecken ein Cutter + Schneidematte</li>
  <li>Lineal und Falzbein (oder ein leerer Kugelschreiber)</li>
  <li>Flüssiger Bastelkleber oder doppelseitiges Klebeband (Klebestift hält nicht)</li>
  <li>Optional: Graupappe (1–1,5 mm) für stabile Räder, 3D-Klebepads</li>
 </ul></div>
 <div class="box"><h3>Richtig drucken</h3><ul>
  <li>Im Druckdialog <b>„Tatsächliche Größe“ / 100 %%</b> wählen, nicht „An Seite anpassen“.</li>
  <li>Auf jedem Blatt ist ein 5-cm-Maßstab: kurz nachmessen.</li>
  <li>Dicken Karton am besten über den hinteren Einzug / das Fach für Sonderpapier drucken.</li>
  <li>Schneideplotter (Cricut, Silhouette, Brother): Die SVG-Dateien im Ordner <i>svg/plotter</i> haben getrennte Ebenen – rot schneiden, blau rillen.</li>
 </ul></div>
 <div class="box"><h3>Linien auf den Vorlagen</h3><div class="legend">
  <div>%s<span>durchgezogen: <b>schneiden</b></span></div>
  <div>%s<span>gestrichelt: <b>rillen und falten</b></span></div>
  <div>%s<span>grau: <b>Klebelasche</b> (Kleber hier drauf)</span></div>
  <div>%s<span>gestrichelter Kreis: hier kommt ein <b>Rad</b> hin</span></div>
 </div></div>
 <div class="box"><h3>Grundtechnik</h3><ul>
  <li><b>Rillen:</b> Lineal an die gestrichelte Linie legen und mit dem Falzbein fest nachziehen – dann bricht der Karton sauber.</li>
  <li><b>Falten:</b> immer so, dass die bedruckte Seite außen bleibt (Ausnahme steht dabei).</li>
  <li><b>Kleben:</b> wenig Kleber auf die Lasche, andrücken und kurz halten. Wäscheklammern helfen.</li>
 </ul></div>
</div>
<h3 style="margin-top:5mm">Welches Blatt wie oft?</h3>
<div class="cols" style="gap:0 6mm">%s%s</div>
<div class="tip"><b>Insgesamt:</b> %d Blätter, davon die Kästchen-Unterteile je 2×. Am besten alles für einen Waggon zusammen ausdrucken und gleich zusammenbauen.</div>
''' % (legend_svg('cut'), legend_svg('fold'), legend_svg('tab'), legend_svg('wheel'),
       tbl(rows[:half]), tbl(rows[half:]), sum(p.copies for p in pages)))

    # ------------------------------------------------ Kaestchen
    cam = Cam(yaw=22, pitch=34)
    g, a = M.box_folding(W1)
    lid_up = M.lid(W2, 5, 0, 0, 80)
    k_lid = render([M.box_bottom(W2, 1.3, 1.3, 0), lid_up], cam, arrows=[((29, -12, 120), (29, -12, 70))])
    filled = render(M.box_closed(W2, 5, 0, 0, 0), cam)
    open_box = render([M.box_bottom(W1, 0, 0, 0)], cam)
    add('''
<div class="head"><h2>Teil 1 · Die 24 Kästchen</h2><span class="tag">Unterteil + Deckel – 4 pro Waggon</span></div>
<div class="steps">%s%s%s%s%s%s</div>
''' % (
        step(1, 'Ausschneiden', 'Unterteile und Deckel entlang der durchgezogenen Linien ausschneiden. Die zwei Unterteile auf einem Blatt greifen ineinander – erst grob trennen, dann genau schneiden.',
             '<div class="thumbs"><div class="thumb">%s</div><div class="thumb" style="flex:0.8">%s</div></div>' % (
                 thumb([part_box_bottom(W1, 0, 0)]), thumb([part_lid(W1, 1, 0, 0)]))),
        step(2, 'Rillen und Ring kleben', 'Alle gestrichelten Linien rillen und vorfalten. Die vier Wände zu einem Ring biegen und die lange Lasche innen an die erste Wand kleben.',
             render(M.box_ring_open(W1), cam)),
        step(3, 'Boden schließen', 'Die drei kleinen Bodenlaschen nach innen knicken und Kleber darauf geben. Den Boden hochklappen und von innen mit einem Stift andrücken.',
             render(g, cam, arrows=a)),
        step(4, 'Unterteil fertig', 'So sieht das fertige Unterteil aus: oben offen, Boden fest. Jetzt alle Unterteile so bauen.', open_box),
        step(5, 'Deckel falten', 'Beim Deckel die vier Ränder nach unten falten und die Ecklaschen innen an die Nachbar-Ränder kleben. Deckel locker aufsetzen.', k_lid),
        step(6, 'Befüllen', 'Kleine Überraschung hinein, Deckel drauf – fertig! Die Zahl auf dem Deckel zeigt den Tag. Die Kästchen 1–4 gehören in Waggon 1, 5–8 in Waggon 2 usw.', filled),
    ))

    # ------------------------------------------------ Waggons
    cam = Cam(yaw=24, pitch=24)
    wA = render(M.wagon_A_only(W1), cam)
    wB = render(M.wagon_B_only(W1), cam)
    wAB = render(M.wagon_model(W1, boxes=False, wheels=False, B_lift=125), cam,
                 arrows=[((-30, 60, 215), (-30, 60, 105))])
    wWheel = render(M.wagon_model(W1, boxes=False, wheels=True, wheel_out=45), cam,
                    arrows=[((28, -42, 20), (28, -8, 20)), ((92, -42, 20), (92, -8, 20))])
    wFull = render(M.wagon_model(W1), cam)
    add('''
<div class="head"><h2>Teil 2 · Die 6 Waggons</h2><span class="tag">je 2 Teile + 4 Räder, oben offen für 4 Kästchen</span></div>
<div class="steps">%s%s%s%s%s%s</div>
''' % (
        step(1, 'Ausschneiden und rillen', 'Teil A (Seitenwände mit Tierfenster + Boden) und Teil B (Zwischenboden mit Stirnwänden) ausschneiden. Alle gestrichelten Linien rillen.',
             '<div class="thumbs"><div class="thumb">%s</div><div class="thumb">%s</div></div>' % (
                 thumb([part_wagon_a(W1, 0, 0)]), thumb([part_wagon_b(W1, 0, 0)]))),
        step(2, 'Teil A falten', 'Die zwei hohen Seitenwände und die zwei niedrigen Stirnklappen nach oben falten. Die Laschen der Seitenwände nach innen knicken und nur unten an die Stirnklappen kleben.', wA),
        step(3, 'Teil B falten', '<b>Achtung, hier anders:</b> Die bedruckten Stirnwände nach oben falten (Druck außen), die hellen Stützen nach unten. So entsteht ein kleiner „Tisch“ mit hohen Enden.', wB),
        step(4, 'Teil B einsetzen', 'Kleber auf die Außenseite der Stützen und auf die oberen Laschen-Enden. Teil B von oben in Teil A schieben: Die Stirnwände von B liegen außen über den Laschen und stehen genau auf den Stirnklappen.', wAB),
        step(5, 'Räder aufkleben', 'Je zwei Räder pro Seite auf die gestrichelten Kreise kleben – sie ragen unten 8 mm über, der Waggon steht auf seinen Rädern. Tipp: Räder vorher auf Graupappe kleben.', wWheel),
        step(6, 'Kästchen einsetzen', 'Vier Kästchen (2 × 2) auf den Zwischenboden stellen. Die Deckel schauen oben heraus. Optional die Radkappen für mehr 3D-Effekt aufkleben.', wFull),
    ))

    # ------------------------------------------------ Lok
    cam = Cam(yaw=28, pitch=24)
    g1, a1 = M.loco_model(1)
    g2, a2 = M.loco_model(2)
    g3, a3 = M.loco_model(3)
    g4, a4 = M.loco_model(4)
    g5, a5 = M.loco_model(5)
    add('''
<div class="head"><h2>Teil 3 · Die Lokomotive</h2><span class="tag">4 gefaltete Teile + Räder</span></div>
<div class="steps">%s%s%s%s%s%s</div>
''' % (
        step(1, 'Fahrgestell', 'Ausschneiden, rillen und die vier Wände nach unten falten. Die Ecklaschen innen an Vorder- und Rückwand kleben. Auf der Oberseite siehst du, wo Kessel und Führerhaus hinkommen.',
             render(g1, cam, arrows=a1)),
        step(2, 'Führerhaus', 'Die Wände zum Häuschen falten, Schlusslasche innen festkleben. Dachlaschen nach innen knicken und das Dach darauf kleben. Bodenlaschen nach innen knicken und das Haus auf das hintere Feld kleben.',
             render(g2, cam, arrows=a2)),
        step(3, 'Kessel rollen', 'Den Kessel über eine Tischkante ziehen, dann rollt er sich leichter. Zur Röhre rollen und mit der Lasche schließen. Vordere Zacken nach innen biegen und den runden Deckel daraufkleben.',
             render(g3, cam, arrows=a3)),
        step(4, 'Kessel und Schornstein', 'Hintere Zacken nach außen biegen. Kessel mit der Naht nach unten auf das Feld kleben und die Zacken ans Führerhaus drücken. Schornstein rollen, untere Zacken nach außen, auf den Kreis kleben.',
             render(g4, cam, arrows=a4)),
        step(5, 'Räder und Rauch', 'Großes Rad hinten, kleines Rad vorne auf die Kreise kleben, auf beiden Seiten. Optional die Treibstange von Rad zu Rad kleben. Die Rauchwolke hinten an den Schornstein kleben.',
             render(g5, cam, arrows=a5)),
        step(6, 'Tipp für die Rundungen', 'Kessel und Schornstein werden am schönsten, wenn du sie vor dem Kleben um einen runden Gegenstand wickelst (Kessel: ca. 6,5 cm, z. B. eine Dose; Schornstein: ca. 2,4 cm, z. B. ein dicker Stift).',
             thumb([part_boiler(0, 0), part_disc(250, 55)])),
    ))

    # ------------------------------------------------ Zusammenbau & Tipps
    train = render(M.train_model(), Cam(yaw=22, pitch=26), pad=10)
    add('''
<div class="head"><h2>Teil 4 · Zug zusammenstellen</h2><span class="tag">und ein paar Tipps</span></div>
<div class="cover-fig" style="height:92mm; margin-top:0">%s</div>
<div class="cols">
 <div class="box"><h3>Reihenfolge</h3>
  <table>
   <tr><td>Lok</td><td>Fuchs</td></tr>
   %s
  </table></div>
 <div class="box"><h3>Kupplungen</h3>
  <p>Die braunen Streifen längs falten. Jeweils ein Ende 1 cm unter den Boden eines Waggons kleben, das andere unter den nächsten – Abstand ca. 2 cm.</p>
  <p>Wenn der Zug nach Weihnachten verstaut werden soll: Kupplung nur an einer Seite festkleben und auf der anderen Seite lose unterschieben.</p></div>
 <div class="box"><h3>Ideen zum Befüllen</h3><ul>
  <li>kleine Schokoladen, Nüsse, Lebkuchenherzen</li>
  <li>Mini-Spielzeug, Sticker, Haarspangen</li>
  <li>Gutscheine („Heute: Kekse backen“, „Vorlesen“)</li>
  <li>gerollte Zettel mit Witzen oder Rätseln</li>
 </ul></div>
 <div class="box"><h3>Damit es lange hält</h3><ul>
  <li>Räder und Kupplungen auf Graupappe kaschieren.</li>
  <li>Unterteile der Kästchen bleiben im Waggon – nur die Deckel werden geöffnet. So kann der Zug jedes Jahr neu befüllt werden.</li>
  <li>Schwere Füllungen (z. B. Nüsse) lieber in die Kästchen, nicht lose in den Waggon.</li>
 </ul></div>
</div>
''' % (train, ''.join('<tr><td>Waggon %d</td><td>%s</td><td>Kästchen %d–%d</td></tr>' % (
        W['n'], W['name'], 4 * W['n'] - 3, 4 * W['n']) for W in WAGONS)))
    return '\n'.join(out)
