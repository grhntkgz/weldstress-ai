"""Check bytes and ZIP members; no training, inference, FE or scientific analysis."""
from pathlib import Path
import csv, hashlib, json, zipfile
ROOT = Path(__file__).resolve().parent
def digest(data):
    return hashlib.sha256(data).hexdigest()
with (ROOT / "MANIFEST_SHA256.csv").open(encoding="utf-8-sig", newline="") as f:
    manifest = list(csv.DictReader(f))
for row in manifest:
    p = (ROOT / row["path"]).resolve()
    if not p.is_relative_to(ROOT) or not p.is_file():
        raise RuntimeError("Missing or unsafe file: " + row["path"])
    if digest(p.read_bytes()) != row["sha256"]:
        raise RuntimeError("SHA-256 mismatch: " + row["path"])
with (ROOT / "SOURCE_PROVENANCE.csv").open(encoding="utf-8-sig", newline="") as f:
    records = list(csv.DictReader(f))
for archive in sorted({r["repository_file"] for r in records}):
    with zipfile.ZipFile(ROOT / archive) as z:
        if z.testzip() is not None:
            raise RuntimeError("ZIP integrity failure: " + archive)
        for row in (r for r in records if r["repository_file"] == archive):
            if digest(z.read(row["archive_member"])) != row["export_SHA256"]:
                raise RuntimeError("Archive-member mismatch: " + row["archive_member"])
print(json.dumps({"status": "PASS", "repository_files": len(manifest), "verified_archive_members": len(records), "research_code_executed": False}, indent=2))
