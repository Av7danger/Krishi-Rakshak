import json
from pathlib import Path
import argparse


CLASS_MAP = {"aphid": 0, "caterpillar": 1, "leaf_spot": 2, "healthy": 3}


def to_yolo_bbox(xmin, ymin, xmax, ymax, w, h):
	cx = (xmin + xmax) / 2 / w
	cy = (ymin + ymax) / 2 / h
	tw = (xmax - xmin) / w
	th = (ymax - ymin) / h
	return cx, cy, tw, th


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--ls-json", type=str, required=True)
	parser.add_argument("--out", type=str, required=True)
	args = parser.parse_args()

	out_dir = Path(args.out)
	out_dir.mkdir(parents=True, exist_ok=True)

	data = json.loads(Path(args.ls_json).read_text(encoding="utf-8"))
	for item in data:
		img_path = Path(item["data"]["image"]).name
		w = item.get("image_width", 320)
		h = item.get("image_height", 320)
		labels = []
		for ann in item.get("annotations", []):
			for r in ann.get("result", []):
				cls = r["value"]["rectanglelabels"][0]
				clsi = CLASS_MAP.get(cls, 0)
				x = r["value"]["x"] * w / 100
				y = r["value"]["y"] * h / 100
				ww = r["value"]["width"] * w / 100
				hh = r["value"]["height"] * h / 100
				xmin, ymin, xmax, ymax = x, y, x + ww, y + hh
				cx, cy, tw, th = to_yolo_bbox(xmin, ymin, xmax, ymax, w, h)
				labels.append(f"{clsi} {cx:.6f} {cy:.6f} {tw:.6f} {th:.6f}")
		(out_dir / (Path(img_path).with_suffix(".txt").name)).write_text("\n".join(labels), encoding="utf-8")
	print(f"Converted {len(data)} items to YOLO format in {out_dir}")


if __name__ == "__main__":
	main()

