import argparse
import os
import random
from pathlib import Path
from PIL import Image, ImageDraw

CLASSES = ["aphid", "caterpillar", "leaf_spot", "healthy"]


def generate_leaf_image(width: int = 320, height: int = 320, pest: str | None = None) -> Image.Image:
	bg_color = (random.randint(20, 60), random.randint(80, 140), random.randint(20, 60))
	img = Image.new("RGB", (width, height), bg_color)
	draw = ImageDraw.Draw(img)
	# Simple veins
	for _ in range(5):
		x0 = random.randint(0, width//2)
		y0 = random.randint(height//4, 3*height//4)
		x1 = width - random.randint(0, width//4)
		y1 = y0 + random.randint(-30, 30)
		draw.line((x0, y0, x1, y1), fill=(40, 120, 40), width=random.randint(2, 5))
	# Optional pest overlay
	if pest and pest != "healthy":
		px, py = random.randint(40, width-40), random.randint(40, height-40)
		size = random.randint(8, 24)
		color = (200, 200, 0) if pest == "aphid" else (120, 60, 20)
		if pest == "leaf_spot":
			color = (150, 30, 30)
			draw.ellipse((px-size, py-size, px+size, py+size), outline=color, width=3)
		else:
			draw.ellipse((px-size, py-size, px+size, py+size), fill=color)
	return img


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--out", type=str, required=True)
	parser.add_argument("--num", type=int, default=40)
	args = parser.parse_args()

	out_dir = Path(args.out)
	out_dir.mkdir(parents=True, exist_ok=True)

	for i in range(args.num):
		cls = random.choice(CLASSES)
		img = generate_leaf_image(pest=cls)
		img.save(out_dir / f"synthetic_{i:03d}_{cls}.png")

	print(f"Wrote {args.num} images to {out_dir}")


if __name__ == "__main__":
	main()
