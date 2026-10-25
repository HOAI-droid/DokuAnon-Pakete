# DokuAnon – Datenpakete

Dieses öffentliche Verzeichnis enthält nur, was DokuAnon aus dem Internet nachlädt:

- **Datenpakete** (unter „Releases“): Sprachmodell für die Namenserkennung, Texterkennung,
  ONNX Runtime und PDFium. DokuAnon lädt sie bei der Einrichtung bzw. über „Laden“ und prüft
  jede Datei mit der SHA-256-Prüfsumme, die fest im Programm steht.
- **`aktuell.json`**: die neueste Version von DokuAnon. Das Programm fragt höchstens einmal am Tag
  danach (abschaltbar) und zeigt nur einen Hinweis – es lädt und installiert nichts selbst.

Das Programm selbst und seine Quelltexte liegen nicht hier.

## Herkunft und Lizenzen

| Paket | Herkunft | Lizenz |
|---|---|---|
| `gliner_multi_pii-v1-q8.zip` | [onnx-community/gliner_multi_pii-v1](https://huggingface.co/onnx-community/gliner_multi_pii-v1), Einbettung auf 8 Bit verkleinert | Apache-2.0 |
| `ppocrv5-mobile-latin.zip` | [PaddlePaddle PP-OCRv5 mobile det](https://huggingface.co/PaddlePaddle/PP-OCRv5_mobile_det_onnx) + [latin rec](https://huggingface.co/PaddlePaddle/latin_PP-OCRv5_mobile_rec_onnx) | Apache-2.0 |
| `onnxruntime-*` | [microsoft/onnxruntime v1.31.0](https://github.com/microsoft/onnxruntime/releases/tag/v1.31.0), unverändert | MIT |
| `pdfium-*` | [bblanchon/pdfium-binaries chromium/7881](https://github.com/bblanchon/pdfium-binaries/releases/tag/chromium%2F7881), unverändert | BSD-3-Clause |

## Pakete neu bauen

Unter „Actions“ → „Pakete veröffentlichen“ → „Run workflow“ mit einer neuen Kennung
(z. B. `pakete-2`). Der Ablauf lädt die Modelle, baut die Pakete mit den Skripten unter
`werkzeuge/`, legt ein Release mit allen Dateien und `SHA256SUMS.txt` an und meldet, ob Größe und
Prüfsumme zu `pakete.toml` passen. Weichen sie ab, müssen die Werte in DokuAnon angepasst werden.
