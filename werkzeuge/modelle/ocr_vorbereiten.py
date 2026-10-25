"""Bereitet das Datenpaket für die Texterkennung vor (nur Entwicklung, wird nicht ausgeliefert).

Modelle (PaddlePaddle, Apache-2.0, offizielle ONNX-Fassungen):
- PP-OCRv5_mobile_det_onnx      – findet Textzeilen im Bild (DB-Verfahren)
- latin_PP-OCRv5_mobile_rec_onnx – liest lateinische Schrift inkl. Umlauten und ß (CTC)

Die Zeichenliste steht in inference.yml; sie wird als zeichen.json abgelegt (das Programm braucht
so keinen YAML-Leser).

Aufruf:  python -I werkzeuge/modelle/ocr_vorbereiten.py [zielordner]
"""

import hashlib
import json
import sys
import urllib.request
from pathlib import Path

QUELLE = "https://huggingface.co/PaddlePaddle/{}/resolve/main/{}"
DATEIEN = {
    "det.onnx": ("PP-OCRv5_mobile_det_onnx", "inference.onnx",
                 "a431985659dc921974177a95adcfbb90fd9e51989a5e04d70d0b75f597b6e61d"),
    "rec.onnx": ("latin_PP-OCRv5_mobile_rec_onnx", "inference.onnx",
                 "7888113072263cb471b93f66dd5e2ad70548dc526fa1ace760d0d973dd121498"),
    "rec.yml": ("latin_PP-OCRv5_mobile_rec_onnx", "inference.yml", None),
}
LIZENZ = """Texterkennung: PP-OCRv5 (PaddlePaddle/PaddleOCR)
https://huggingface.co/PaddlePaddle/PP-OCRv5_mobile_det_onnx
https://huggingface.co/PaddlePaddle/latin_PP-OCRv5_mobile_rec_onnx
Lizenz: Apache License 2.0 – https://www.apache.org/licenses/LICENSE-2.0
"""


def zeichenliste(yml: str) -> list[str]:
    """`character_dict` aus inference.yml (eine Liste einfacher Zeichen)."""
    zeichen, drin = [], False
    for zeile in yml.splitlines():
        if zeile.startswith("  character_dict:"):
            drin = True
            continue
        if drin:
            if not zeile.startswith("  - "):
                break
            w = zeile[4:]
            if len(w) >= 2 and w[0] == w[-1] and w[0] in "'\"":
                w = w[1:-1].replace("''", "'") if w[0] == "'" else json.loads(w)
            zeichen.append(w)
    return zeichen


def main() -> None:
    ziel = Path(sys.argv[1] if len(sys.argv) > 1 else "target/modelle/ppocrv5")
    ziel.mkdir(parents=True, exist_ok=True)
    for name, (repo, datei, sha) in DATEIEN.items():
        pfad = ziel / name
        if not pfad.exists():
            print("lade", repo, datei, flush=True)
            urllib.request.urlretrieve(QUELLE.format(repo, datei), pfad)
        if sha and hashlib.sha256(pfad.read_bytes()).hexdigest() != sha:
            sys.exit(f"Prüfsumme von {name} stimmt nicht")
    zeichen = zeichenliste((ziel / "rec.yml").read_text(encoding="utf-8"))
    if len(zeichen) < 100 or "ä" not in zeichen or "ß" not in zeichen:
        sys.exit(f"Zeichenliste unvollständig ({len(zeichen)})")
    (ziel / "zeichen.json").write_text(json.dumps(zeichen, ensure_ascii=False), encoding="utf-8")
    (ziel / "rec.yml").unlink()
    (ziel / "LIZENZ.txt").write_text(LIZENZ, encoding="utf-8")
    print(f"{ziel}: {len(zeichen)} Zeichen, fertig")


main()
