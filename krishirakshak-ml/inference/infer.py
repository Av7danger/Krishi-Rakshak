import argparse
import json
from PIL import Image
import requests


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("image", type=str)
	parser.add_argument("--url", type=str, default="http://localhost:8000/predict")
	args = parser.parse_args()

	with open(args.image, "rb") as f:
		files = {"file": (args.image, f, "image/png")}
		r = requests.post(args.url, files=files, timeout=30)
		print(json.dumps(r.json(), indent=2))


if __name__ == "__main__":
	main()

