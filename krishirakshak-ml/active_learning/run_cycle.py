import argparse
from pathlib import Path
import subprocess


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--k", type=int, default=10)
	args = parser.parse_args()

	subprocess.run(["python", "active_learning/prepare_al_batch.py", "--k", str(args.k)], check=True)
	print("Submit al_batch.json to Label Studio, then export to data/labeled/export.json")
	print("After labeling, run labeling/label_conversion.py and retrain.")


if __name__ == "__main__":
	main()

