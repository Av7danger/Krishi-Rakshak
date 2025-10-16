import json
from pathlib import Path
from datetime import datetime

REGISTRY_DIR = Path("krishirakshak-ml/registry/store")
REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
INDEX = REGISTRY_DIR / "index.json"


def load_index():
	if INDEX.exists():
		return json.loads(INDEX.read_text(encoding="utf-8"))
	return {"models": []}


def save_index(idx):
	INDEX.write_text(json.dumps(idx, indent=2), encoding="utf-8")


def register_model(artifacts_dir: Path):
	idx = load_index()
	model_id = artifacts_dir.name
	entry = {
		"id": model_id,
		"path": str(artifacts_dir.resolve()),
		"date": datetime.utcnow().isoformat() + "Z",
	}
	idx["models"].append(entry)
	save_index(idx)
	(REGISTRY_DIR / "latest").write_text(model_id, encoding="utf-8")
	return model_id


def latest_model_path() -> Path | None:
	if not (REGISTRY_DIR / "latest").exists():
		return None
	mid = (REGISTRY_DIR / "latest").read_text(encoding="utf-8").strip()
	p = Path("krishirakshak-ml/artifacts") / mid
	return p if p.exists() else None
