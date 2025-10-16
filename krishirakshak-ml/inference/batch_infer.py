import argparse
import json
from pathlib import Path
import requests


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--images", type=str, required=True)
	parser.add_argument("--out", type=str, required=True)
	parser.add_argument("--url", type=str, default="http://localhost:8000/predict")
	args = parser.parse_args()

	imgs = sorted(list(Path(args.images).glob("*.png")) + list(Path(args.images).glob("*.jpg")))
	outp = Path(args.out)
	with outp.open("w", encoding="utf-8") as fout:
		for p in imgs:
			with p.open("rb") as f:
				r = requests.post(args.url, files={"file": (p.name, f, "image/png")}, timeout=30)
				fout.write(json.dumps({"image": p.name, "result": r.json()}) + "\n")
	print(f"Wrote results to {outp}")


if __name__ == "__main__":
	main()

