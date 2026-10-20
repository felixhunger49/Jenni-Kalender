# Schönere Tierbilder mit ComfyUI

`tierportraets_workflow.json` erzeugt in einem Durchlauf alle 7 Tierporträts (Fuchs, Löwe, Bär, Hase, Pinguin, Otter, Giraffe) im Stil des Fotos: weiches Aquarell, Pastell (Salbeigrün, Altrosa, Creme), Mütze/Schal, heller Cremehintergrund – der passt genau zur Fensterfarbe der Vorlage, darum ist kein Freistellen nötig.

## Benötigtes Modell

| Datei | Ordner in ComfyUI | Quelle | Größe |
|---|---|---|---|
| `sd_xl_base_1.0.safetensors` | `ComfyUI/models/checkpoints/` | https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0 (Reiter „Files“) | ca. 6,9 GB |

Mehr braucht es nicht: nur Standard-Nodes, keine Custom Nodes, kein LoRA. Läuft ab ca. 8 GB Grafikspeicher (NVIDIA) oder auf Apple Silicon mit 16 GB.

Optional, oft schöner für Kinderbuch-Stil: ein anderes SDXL-Checkpoint (z. B. ein Illustrations-Modell von Civitai). Dann im Node „Modell (SDXL)“ einfach die Datei umstellen.

## Benutzen

1. ComfyUI starten, `tierportraets_workflow.json` ins Fenster ziehen.
2. Im Node „Modell (SDXL)“ prüfen, dass `sd_xl_base_1.0.safetensors` ausgewählt ist.
3. **Queue / Run** drücken. Die Bilder landen in `ComfyUI/output/` als `tier_fuchs_00001_.png` usw.
4. Gefällt ein Tier nicht: im KSampler dieses Tieres den `seed` ändern (oder auf `randomize`) und nur neu starten – die anderen bleiben gleich.

`tierportraets_api.json` ist derselbe Workflow im API-Format (für Skripte / `POST /prompt`).
`erzeuge_workflow.py` erzeugt beide Dateien neu, falls du Prompts, Seed, Schritte oder Modell ändern willst.

## In die Vorlagen einbauen

1. Die fertigen PNGs in den Ordner `tiere/` im Repo legen (Dateiname muss den Tiernamen enthalten, z. B. `tier_fuchs_00001_.png`).
2. `python3 tools/build.py` ausführen.

Das Bild ersetzt dann das gezeichnete Tier in den Fenstern – in den Druckvorlagen, den SVGs und den Bildern der Anleitung. Fehlt ein Bild, bleibt das gezeichnete Tier. Das Bild wird auf das Fenster zugeschnitten (oben/unten etwas weg), der Kopf sollte also mittig sein.
