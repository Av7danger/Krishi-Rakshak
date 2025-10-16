import argparse
import json
import os
from pathlib import Path
import requests
from dotenv import load_dotenv


def main():
	load_dotenv()
	parser = argparse.ArgumentParser()
	parser.add_argument("--mock", type=str, default="tests/feedback.json")
	parser.add_argument("--out", type=str, default="data/labeled")
	args = parser.parse_args()

	url = os.getenv("BACKEND_FEEDBACK_URL", "")
	if url:
		r = requests.get(url, headers={"Authorization": f"Bearer {os.getenv('BACKEND_API_TOKEN','')}"}, timeout=30)
		data = r.json()
	else:
		data = json.loads(Path(args.mock).read_text(encoding="utf-8")) if Path(args.mock).exists() else []

	out_dir = Path(args.out)
	out_dir.mkdir(parents=True, exist_ok=True)
	for item in data:
		img_name = Path(item["image"]).name
		labels = []
		for d in item.get("detections", []):
			x1, y1, x2, y2 = d["bbox_xyxy"]
			w = item.get("width", 320)
			h = item.get("height", 320)
			cx = (x1 + x2) / 2 / w
			cy = (y1 + y2) / 2 / h
			tw = (x2 - x1) / w
			th = (y2 - y1) / h
			cls = d.get("cls_id", 0)
			labels.append(f"{cls} {cx:.6f} {cy:.6f} {tw:.6f} {th:.6f}")
		(out_dir / img_name.replace(".png", ".txt")).write_text("\n".join(labels), encoding="utf-8")
	print(f"Ingested {len(data)} feedback items into {out_dir}")


if __name__ == "__main__":
	main()

