"""Stellt alle Datenpakete in einem Ordner zusammen (nur Entwicklung).

Der Ordner ist zugleich
- der Inhalt der Paketquelle (alles dort hochladen, Adresse in pakete.toml unter `quelle`) und
- das Offline-Komplettpaket (`dokuanon-cli pakete-laden --aus <ordner>`).

Fremde Pakete (ONNX Runtime, PDFium) werden unverändert von GitHub übernommen und geprüft.
Das GLiNER-Paket wird aus dem vorbereiteten Modellordner gebaut (gliner_vorbereiten.py),
reproduzierbar: feste Zeitstempel, feste Reihenfolge.

Aufruf:  python -I werkzeuge/pakete_bauen.py <zielordner> [ordner mit den Modellordnern]
Am Ende werden Größe und SHA-256 jedes Pakets ausgegeben – sie müssen zu pakete.toml passen.
"""

import hashlib
import sys
import tomllib
import urllib.request
import zipfile
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
HERKUNFT = {
    "onnxruntime-win-x64-1.31.0.zip": "https://github.com/microsoft/onnxruntime/releases/download/v1.31.0/",
    "onnxruntime-linux-x64-1.31.0.tgz": "https://github.com/microsoft/onnxruntime/releases/download/v1.31.0/",
    "onnxruntime-osx-arm64-1.31.0.tgz": "https://github.com/microsoft/onnxruntime/releases/download/v1.31.0/",
    "pdfium-win-x64.tgz": "https://github.com/bblanchon/pdfium-binaries/releases/download/chromium%2F7881/",
    "pdfium-linux-x64.tgz": "https://github.com/bblanchon/pdfium-binaries/releases/download/chromium%2F7881/",
    "pdfium-mac-arm64.tgz": "https://github.com/bblanchon/pdfium-binaries/releases/download/chromium%2F7881/",
}
# Selbst gebaute Pakete: Paketname → (Modellordner unter target/modelle, Dateien)
MODELL_PAKETE = {
    "gliner": ("gliner_multi_pii-v1", ["gliner_config.json", "tokenizer.json", "tokenizer_config.json",
                                       "special_tokens_map.json", "added_tokens.json",
                                       "onnx/model_einbettung_q8.onnx"]),
    "ocr": ("ppocrv5", ["det.onnx", "rec.onnx", "zeichen.json", "LIZENZ.txt"]),
}


def sha256(pfad: Path) -> str:
    h = hashlib.sha256()
    with pfad.open("rb") as f:
        while block := f.read(1 << 20):
            h.update(block)
    return h.hexdigest()


def modell_zip(modell: Path, dateien: list[str], ziel: Path) -> None:
    """Reproduzierbar: feste Zeitstempel und Reihenfolge."""
    with zipfile.ZipFile(ziel, "w") as z:
        for name in dateien:
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            with (modell / name).open("rb") as quelle, z.open(info, "w") as aus:
                while block := quelle.read(1 << 20):
                    aus.write(block)


def main() -> None:
    ziel = Path(sys.argv[1])
    modelle = Path(sys.argv[2]) if len(sys.argv) > 2 else WURZEL / "target/modelle"
    ziel.mkdir(parents=True, exist_ok=True)
    manifest = tomllib.loads((WURZEL / "pakete.toml").read_text(encoding="utf-8"))
    fehler = 0
    for p in manifest.get("paket", []):
        pfad = ziel / p["datei"]
        if not pfad.exists():
            if p["datei"] in HERKUNFT:
                print("lade", p["datei"], flush=True)
                urllib.request.urlretrieve(HERKUNFT[p["datei"]] + p["datei"], pfad)
            elif p["name"] in MODELL_PAKETE:
                ordner, dateien = MODELL_PAKETE[p["name"]]
                print("baue", p["datei"], flush=True)
                modell_zip(modelle / ordner, dateien, pfad)
            else:
                print("unbekannte Herkunft:", p["datei"])
                fehler += 1
                continue
        groesse, h = pfad.stat().st_size, sha256(pfad)
        passt = groesse == p["groesse"] and h == p["sha256"]
        print(f"{'ok ' if passt else 'ABWEICHUNG'} {p['datei']}: groesse = {groesse}, sha256 = \"{h}\"")
        fehler += not passt
    sys.exit(1 if fehler else 0)


main()
