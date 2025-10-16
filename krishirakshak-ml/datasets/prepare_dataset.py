import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import List

import yaml
from sklearn.model_selection import train_test_split


def compute_md5(path: Path) -> str:
	m = hashlib.md5()
	with open(path, "rb") as f:
		for chunk in iter(lambda: f.read(8192), b""):
			m.update(chunk)
	return m.hexdigest()


def discover_images(raw_dir: Path) -> List[Path]:
	images = []
	for ext in ("*.jpg", "*.jpeg", "*.png"):
		images.extend(raw_dir.rglob(ext))
	return images


def write_ultralytics_yaml(build_dir: Path, train_dir: Path, val_dir: Path, classes: List[str]):
	data = {
		"path": str(build_dir.resolve()),
		"train": str(train_dir.relative_to(build_dir)),
		"val": str(val_dir.relative_to(build_dir)),
		"names": {i: c for i, c in enumerate(classes)},
	}
	with open(build_dir / "data.yaml", "w", encoding="utf-8") as f:
		yaml.safe_dump(data, f)


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--data-config", type=str, required=True)
	parser.add_argument("--out", type=str, required=True)
	args = parser.parse_args()

	with open(args.data_config, "r", encoding="utf-8") as f:
		cfg = yaml.safe_load(f)

	raw_dir = Path(cfg.get("raw_dir", "data/raw"))
	build_dir = Path(args.out)
	train_dir = build_dir / "images/train"
	val_dir = build_dir / "images/val"
	labels_train = build_dir / "labels/train"
	labels_val = build_dir / "labels/val"
	for d in [train_dir, val_dir, labels_train, labels_val]:
		d.mkdir(parents=True, exist_ok=True)

	classes = cfg["classes"]
	images = discover_images(raw_dir)
	if not images:
		raise SystemExit(f"No images found in {raw_dir}. Generate synthetic data first.")

	train_paths, val_paths = train_test_split(images, test_size=cfg.get("val_split", 0.2), random_state=42)

	manifest = {"classes": classes, "counts": {c: 0 for c in classes}, "files": [], "consent_default": bool(cfg.get("consent_default", True))}

	def copy_and_stub_labels(paths: List[Path], out_img_dir: Path, out_lbl_dir: Path):
		for p in paths:
			# YOLO txt label stub: 0 0.5 0.5 1.0 1.0 for demo, or empty for healthy
			fname = p.name
			cls_name = None
			for c in classes:
				if f"_{c}." in fname:
					cls_name = c
					break
			out_path = out_img_dir / fname
			out_path.write_bytes(p.read_bytes())
			lbl_name = (out_lbl_dir / fname).with_suffix(".txt")
			if cls_name and cls_name != "healthy":
				cls_idx = classes.index(cls_name)
				lbl_name.write_text(f"{cls_idx} 0.5 0.5 0.6 0.6\n", encoding="utf-8")
				manifest["counts"][cls_name] += 1
			else:
				lbl_name.write_text("", encoding="utf-8")
			manifest["files"].append({
				"file": str(out_path.resolve()),
				"label": str(lbl_name.resolve()),
				"checksum": compute_md5(out_path),
				"consent": bool(cfg.get("consent_default", True)),
			})

	copy_and_stub_labels(train_paths, train_dir, labels_train)
	copy_and_stub_labels(val_paths, val_dir, labels_val)

	write_ultralytics_yaml(build_dir, train_dir, val_dir, classes)

	with open(build_dir / "manifest.json", "w", encoding="utf-8") as f:
		json.dump(manifest, f, indent=2)

	print(f"Prepared dataset at {build_dir}. Train: {len(train_paths)}, Val: {len(val_paths)}")


if __name__ == "__main__":
	main()
