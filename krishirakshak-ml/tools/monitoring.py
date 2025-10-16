import argparse
import json
from pathlib import Path
from PIL import Image
import numpy as np
from scipy.stats import ks_2samp


def stats_for_folder(folder: Path):
	files = list(folder.glob("*.png")) + list(folder.glob("*.jpg"))
	means = []
	sizes = []
	for p in files[:100]:
		img = Image.open(p).convert("L")
		arr = np.array(img)
		means.append(arr.mean())
		sizes.append(arr.size)
	return {"count": len(files), "mean_brightness": float(np.mean(means) if means else 0), "sizes": sizes[:10]}


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--baseline", type=str, required=True)
	parser.add_argument("--recent", type=str, required=True)
	parser.add_argument("--out", type=str, default="monitoring")
	args = parser.parse_args()

	b = stats_for_folder(Path(args.baseline))
	r = stats_for_folder(Path(args.recent))
	ks = ks_2samp([b["mean_brightness"]], [r["mean_brightness"]]).statistic if b["count"] and r["count"] else 0
	alert = ks > 0.5
	Path(args.out).mkdir(parents=True, exist_ok=True)
	(Path(args.out) / "drift.json").write_text(json.dumps({"baseline": b, "recent": r, "ks_stat": ks, "alert": alert}, indent=2), encoding="utf-8")
	print(f"Drift alert: {alert}")


if __name__ == "__main__":
	main()

