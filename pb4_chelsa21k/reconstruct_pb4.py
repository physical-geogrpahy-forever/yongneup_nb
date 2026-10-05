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
expected = "eb55c8896ba1290c605debd912c64bc603832e7352eb8ad35f2623a214eff01d"
print(f"wrote: {out}")
print(f"sha256: {sha}")
if sha != expected:
    raise SystemExit(f"SHA-256 mismatch: expected {expected}")
print("SHA-256 OK")