from pathlib import Path
import base64, hashlib

ROOT = Path(__file__).resolve().parent
PARTS = sorted((ROOT / "payload").glob("PB4Studio_v6.6.3_CHELSA21K.zip.b64.part*"))
if not PARTS:
    raise SystemExit("PB4 base64 parts not found")
encoded = "".join(p.read_text(encoding="ascii").strip() for p in PARTS)
out = ROOT / "PB4Studio_v6.6.3_CHELSA21K.zip"
out.write_bytes(base64.b64decode(encoded, validate=True))
sha = hashlib.sha256(out.read_bytes()).hexdigest()
expected = "0f0168cfa29277e30fe7707c2d450bd6a613a502f7e048ffce6d96e40d52d8a4"
print(f"wrote: {out}")
print(f"sha256: {sha}")
if sha != expected:
    raise SystemExit(f"SHA-256 mismatch: expected {expected}")
print("SHA-256 OK")