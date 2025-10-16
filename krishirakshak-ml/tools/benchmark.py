import argparse
import json
import time
from pathlib import Path


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--artifacts", type=str, required=True)
	parser.add_argument("--out", type=str, default="benchmarks")
	args = parser.parse_args()

	art = Path(args.artifacts)
	onnx = art / "model.onnx"
	tfl = art / "model.tflite"

	# Simulated latency measurement
	start = time.time(); time.sleep(0.01); latency = (time.time() - start) * 1000

	Path(args.out).mkdir(parents=True, exist_ok=True)
	data = {
		"model_id": art.name,
		"sizes": {
			"onnx": onnx.stat().st_size if onnx.exists() else 0,
			"tflite": tfl.stat().st_size if tfl.exists() else 0,
		},
		"latency_ms": latency,
	}
	(out := Path(args.out) / f"{art.name}.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
	print(f"Wrote {out}")


if __name__ == "__main__":
	main()

