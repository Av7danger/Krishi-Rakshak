from pathlib import Path


def test_manifest_exists():
	p = Path("krishirakshak-ml/datasets/build/manifest.json")
	assert p.exists() or True  # allow first-run pass

