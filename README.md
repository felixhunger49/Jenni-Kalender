# Eisenbahn-Adventskalender

Bastelvorlage für einen Adventskalender-Zug: eine Lok und 4 Waggons, oben offen und ohne Zwischenboden, in jedem Waggon 6 Kästchen mit den Zahlen 1–24. Tiere: Pinguin (Lok), Löwe, Bär, Giraffe, Elefant – sie schauen aus den Fenstern.

## Dateien

| Datei | Inhalt |
|---|---|
| `ausgabe/Anleitung-Eisenbahn-Adventskalender.pdf` | Bebilderte Schritt-für-Schritt-Anleitung (6 Seiten): Material, Drucktipps, Kästchen, Waggons, Lok, Zusammenstellen |
| `ausgabe/Vorlagen-Eisenbahn-Adventskalender.pdf` | 34 farbige Druckvorlagen A4 in Originalgröße, jedes Blatt 1× |
| `ausgabe/svg/druck/` | jede Vorlage als SVG mit den Ebenen *Druck*, *Schneiden*, *Falzen* |
| `ausgabe/svg/plotter/` | nur Schnitt- (rot) und Rilllinien (blau) für Schneideplotter |

Drucken mit **„Tatsächliche Größe“ / 100 %** auf Karton mit 250–300 g/m². Jede Vorlage hat einen 5-cm-Maßstab zum Nachmessen.

## Maße

- Kästchen: 4,2 × 3,7 cm innen, 9 cm hoch, angesetzter Klappdeckel mit Einsteckzunge und Zahl
- Waggon: Grundfläche 9 × 12 cm, alle Wände 8 cm hoch (+ 8 mm Räder); 6 Kästchen (2 × 3) stehen direkt auf dem Boden und schauen gut 1 cm heraus
- Lok: ca. 18 × 9 cm, ca. 19 cm hoch mit Rauchwolke

## Aufbau mit wenigen Teilen

- **Waggon:** nur 2 gefaltete Teile. Teil A = Boden + zwei Stirnwände + eine lange Wand, Teil B = die zweite lange Wand. Die Räder sind an den langen Wänden angesetzt.
- **Lok:** Fahrgestell (mit angesetzten Rädern), Führerhaus (mit Dach), Kessel (+ runder Deckel) und Schornstein, je aus einem Stück. Optional Rauchwolke, Treibstangen, Kupplungen.
- **Kästchen:** ein Stück mit Klappdeckel.

## Tierbilder

Die Originalbilder liegen in `tiere/original/`, `python3 tools/freistellen.py` stellt sie frei und legt sie als `tiere/<name>.png` ab. Der Generator setzt sie so ins Fenster, dass die Pfoten auf der Fensterbank liegen.

## Neu erzeugen

```bash
python3 tools/build.py            # schreibt nach ./ausgabe
```

Benötigt Python 3 und Node mit Playwright (Chromium) für den PDF-Druck. Die Geometrie steht in `tools/zug.py` (alle Maße in mm), das Seitenlayout in `tools/vorlagen.py`, die Anleitung in `tools/anleitung.py`, die 3D-Bilder der Anleitung in `tools/modelle.py` und `tools/iso.py`.

Schriften: Patrick Hand und Nunito (SIL Open Font License) in `fonts/`.
