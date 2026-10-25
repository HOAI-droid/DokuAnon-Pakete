"""Bereitet das GLiNER-Datenpaket vor (nur Entwicklung, wird nicht ausgeliefert).

Lädt `onnx-community/gliner_multi_pii-v1` (ONNX-Fassung von `urchade/gliner_multi_pii-v1`,
Apache-2.0) und verkleinert NUR die Einbettungstabelle auf 8 Bit (Gather-Knoten). Die
Rechenschichten bleiben in voller Genauigkeit:

- fertige int8-Fassung (alles quantisiert): höchste Sicherheit auf deutschem Testtext 0,26 – unbrauchbar
- nur MatMul quantisiert: 0,43 – unbrauchbar
- nur Einbettung quantisiert: wie das Original (Person 0,999), 581 MB statt 1,1 GB

Aufruf:  python -I werkzeuge/modelle/gliner_vorbereiten.py <zielordner>
Braucht: pip install onnx onnxruntime
"""

import hashlib
import os
import sys
import urllib.request
from pathlib import Path

# ONNX Runtime sendet sonst Nutzungsdaten an Microsoft (auch die Python-Fassung)
os.environ["ORT_DISABLE_TELEMETRY"] = "1"

from onnxruntime.quantization import QuantType, quantize_dynamic

QUELLE = "https://huggingface.co/onnx-community/gliner_multi_pii-v1/resolve/main/"
DATEIEN = ["gliner_config.json", "tokenizer.json", "tokenizer_config.json", "special_tokens_map.json",
           "added_tokens.json", "onnx/model.onnx"]

ziel = Path(sys.argv[1] if len(sys.argv) > 1 else "target/modelle/gliner_multi_pii-v1")
(ziel / "onnx").mkdir(parents=True, exist_ok=True)
for name in DATEIEN:
    pfad = ziel / name
    if not pfad.exists():
        print("lade", name, flush=True)
        urllib.request.urlretrieve(QUELLE + name, pfad)

quelle = ziel / "onnx" / "model.onnx"
klein = ziel / "onnx" / "model_einbettung_q8.onnx"
quantize_dynamic(str(quelle), str(klein), weight_type=QuantType.QUInt8, per_channel=False,
                 op_types_to_quantize=["Gather"])
quelle.unlink()  # nur die kleine Fassung behalten
h = hashlib.sha256(klein.read_bytes()).hexdigest()
print(f"{klein}: {klein.stat().st_size} Bytes, SHA-256 {h}")
