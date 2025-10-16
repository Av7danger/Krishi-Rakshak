import argparse
import os
from pathlib import Path
import time
import yaml
from dotenv import load_dotenv

try:
	from ultralytics import YOLO
	ULTRA = True
except Exception:
	ULTRA = False

try:
	import mlflow
	MLF = True
except Exception:
	MLF = False


def train_with_ultralytics(config_path: str, smoke: bool = False):
	with open(config_path, "r", encoding="utf-8") as f:
		cfg = yaml.safe_load(f)
	data_yaml = Path("datasets/build/data.yaml")
	if not data_yaml.exists():
		raise SystemExit("datasets/build/data.yaml not found. Run dataset preparation.")

	model_name = cfg.get("model", "yolov8n.pt")
	epochs = 1 if smoke else int(cfg.get("epochs", 2))
	batch = int(cfg.get("batch", 8))
	imgsz = int(cfg.get("imgsz", 320))

	if not ULTRA:
		print("Ultralytics not available, simulating training for smoke...")
		time.sleep(1)
		return {"run_id": "simulated", "best": "artifacts/simulated/best.pt"}

	model = YOLO(model_name)
	results = model.train(
		data=str(data_yaml),
		epochs=epochs,
		imgsz=imgsz,
		batch=batch,
		project="runs/train",
		name="exp",
		save=True,
	)
	best = results.save_dir / "weights/best.pt"
	return {"run_id": results.save_dir.name, "best": str(best)}


def main():
	load_dotenv()
	parser = argparse.ArgumentParser()
	parser.add_argument("--config", type=str, required=True)
	parser.add_argument("--smoke", action="store_true")
	args = parser.parse_args()

	if MLF:
		mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "./registry/mlruns"))
		mlflow.set_experiment(os.getenv("MLFLOW_EXPERIMENT_NAME", "krishirakshak"))
		with mlflow.start_run() as run:
			info = train_with_ultralytics(args.config, args.smoke)
			mlflow.log_params({"config": Path(args.config).name, "smoke": args.smoke})
			mlflow.log_artifact(args.config)
			print(f"Run completed. Run ID: {run.info.run_id}")
	else:
		info = train_with_ultralytics(args.config, args.smoke)
		print("Run completed (no MLflow).", info)


if __name__ == "__main__":
	main()
