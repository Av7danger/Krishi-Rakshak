from pathlib import Path
import json


def test_unique_selection(tmp_path):
	# Simulate AL selection output
	items = [{"data": {"image": f"/x/{i}.png"}} for i in range(5)]
	p = tmp_path / "al_batch.json"
	p.write_text(json.dumps(items), encoding="utf-8")
	paths = [it["data"]["image"] for it in items]
	assert len(paths) == len(set(paths))
