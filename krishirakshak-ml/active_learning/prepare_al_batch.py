import argparse
from pathlib import Path
import json
import random


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--unlabeled", type=str, default="data/raw")
	parser.add_argument("--out", type=str, default="active_learning/export")
	parser.add_argument("--k", type=int, default=10)
	args = parser.parse_args()

	unl = sorted([p for p in Path(args.unlabeled).glob("*.png")])
	sel = random.sample(unl, min(args.k, len(unl)))
	out_dir = Path(args.out)
	out_dir.mkdir(parents=True, exist_ok=True)

	# Create simple Label Studio import JSON
	items = [{"data": {"image": str(p.resolve())}} for p in sel]
	with open(out_dir / "al_batch.json", "w", encoding="utf-8") as f:
		json.dump(items, f, indent=2)
	print(f"Prepared {len(sel)} items for labeling at {out_dir}")


if __name__ == "__main__":
	main()

