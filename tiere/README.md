# Eigene Tierbilder

Lege hier Bilder ab, deren Dateiname den Tiernamen enthält, z. B. `fuchs.png` oder `tier_fuchs_00001_.png`
(so speichert sie der ComfyUI-Workflow in `comfyui/`). Erkannte Namen:

`fuchs` (Lok), `loewe`, `baer`, `hase`, `pinguin`, `otter`, `giraffe`

Danach `python3 tools/build.py` ausführen: Das Bild ersetzt das gezeichnete Tier im Fenster
(Druckvorlagen, SVGs und Anleitungsbilder). Quadratische Bilder mit hellem Cremehintergrund passen am besten;
oben und unten wird etwas abgeschnitten. Fehlt ein Bild, bleibt das gezeichnete Tier.
