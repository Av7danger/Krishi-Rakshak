import argparse
from pathlib import Path
import numpy as np

try:
	import tensorflow as tf  # type: ignore
	TF_OK = True
except Exception:
	TF_OK = False


def representative_dataset_gen(calib_dir: Path, img_size: int = 320):
	import PIL.Image as Image
	images = list(calib_dir.glob("*.png")) + list(calib_dir.glob("*.jpg"))
	for p in images[:50]:
		img = Image.open(p).convert("RGB").resize((img_size, img_size))
		arr = np.array(img, dtype=np.float32) / 255.0
		arr = np.expand_dims(arr, 0)
		yield [arr]


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--artifacts", type=str, required=True)
	parser.add_argument("--mode", type=str, choices=["dynamic", "static"], default="dynamic")
	parser.add_argument("--calib", type=str, default="datasets/build/images/train")
	parser.add_argument("--imgsz", type=int, default=320)
	args = parser.parse_args()

	art_dir = Path(args.artifacts)
	tfl_path = art_dir / "model.tflite"
	onnx_path = art_dir / "model.onnx"  # if needed for future ONNX->TFLite

	if not TF_OK:
		print("TensorFlow not available; writing placeholder TFLite file.")
		if not tfl_path.exists():
			tfl_path.write_bytes(b"placeholder")
		return

	# Example: quantize an existing float model (assume SavedModel or Keras model exists).
	# In this scaffold we demonstrate converter config only and keep a placeholder if model missing.
	if not tfl_path.exists():
		# Create a tiny dummy model and convert to show pipeline works.
		model = tf.keras.Sequential([tf.keras.layers.Input((args.imgsz, args.imgsz, 3)), tf.keras.layers.Flatten(), tf.keras.layers.Dense(2)])
		converter = tf.lite.TFLiteConverter.from_keras_model(model)
		if args.mode == "dynamic":
			converter.optimizations = [tf.lite.Optimize.DEFAULT]
			tfl = converter.convert()
			tfl_path.write_bytes(tfl)
			print(f"Wrote dynamic int8-ready TFLite to {tfl_path}")
		else:
			converter.optimizations = [tf.lite.Optimize.DEFAULT]
			converter.representative_dataset = lambda: representative_dataset_gen(Path(args.calib), args.imgsz)
			converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
			converter.inference_input_type = tf.uint8
			converter.inference_output_type = tf.uint8
			tfl = converter.convert()
			tfl_path.write_bytes(tfl)
			print(f"Wrote static int8 TFLite to {tfl_path}")
	else:
		print(f"Existing TFLite found at {tfl_path}; skip.")


if __name__ == "__main__":
	main()

