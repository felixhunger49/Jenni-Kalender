# Eisenbahn-Adventskalender

Bastelvorlage für einen Adventskalender-Zug: eine Lok und 6 Waggons, oben offen, in jedem Waggon 4 Kästchen mit den Zahlen 1–24.

## Dateien

| Datei | Inhalt |
|---|---|
| `ausgabe/Anleitung-Eisenbahn-Adventskalender.pdf` | Bebilderte Schritt-für-Schritt-Anleitung (6 Seiten): Material, Drucktipps, Kästchen, Waggons, Lok, Zusammenstellen |
| `ausgabe/Vorlagen-Eisenbahn-Adventskalender.pdf` | 29 farbige Druckvorlagen A4 in Originalgröße (Kästchen-Unterteile je 2× drucken → 35 Blatt) |
| `ausgabe/svg/druck/` | jede Vorlage als SVG mit den Ebenen *Druck*, *Schneiden*, *Falzen* |
| `ausgabe/svg/plotter/` | nur Schnitt- (rot) und Rilllinien (blau) für Schneideplotter |

Drucken mit **„Tatsächliche Größe“ / 100 %** auf Karton mit 250–300 g/m². Jede Vorlage hat einen 5-cm-Maßstab zum Nachmessen.

## Maße

- Kästchen: 5,5 × 5,5 × 5,5 cm innen, Stülpdeckel mit Zahl
- Waggon: 12 × 12 cm, 8 cm Wandhöhe (+ 8 mm Räder); die Kästchen stehen auf einem Zwischenboden und schauen gut 1 cm heraus
- Lok: ca. 19 × 9 cm, ca. 18 cm hoch mit Rauchwolke

## Aufbau mit wenigen Teilen

- **Waggon:** nur 2 gefaltete Teile. Teil A = Boden + Seitenwände + niedrige Stirnklappen, Teil B = Zwischenboden mit Stirnwänden und Stützen. Dazu 4 Räder.
- **Lok:** Fahrgestell, Führerhaus (mit Dach), Kessel (+ runder Deckel) und Schornstein, je aus einem Stück. Dazu 4 Räder, optional Rauchwolke und Treibstangen.
- **Kästchen:** Unterteil (ein Stück) + Deckel (ein Stück).

## Neu erzeugen

```bash
python3 tools/build.py            # schreibt nach ./ausgabe
```

Benötigt Python 3 und Node mit Playwright (Chromium) für den PDF-Druck. Die Geometrie steht in `tools/zug.py` (alle Maße in mm), das Seitenlayout in `tools/vorlagen.py`, die Anleitung in `tools/anleitung.py`, die 3D-Bilder der Anleitung in `tools/modelle.py` und `tools/iso.py`.

Schriften: Patrick Hand und Nunito (SIL Open Font License) in `fonts/`.
