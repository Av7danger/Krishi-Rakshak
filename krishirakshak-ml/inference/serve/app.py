from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from PIL import Image
import io
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="KrishiRakshak-ML Inference")

# Optional Prometheus-style metrics endpoint (lightweight)
_REQS = 0
_ERRS = 0

try:
	from ultralytics import YOLO
	YOLO_OK = True
	_model = None
except Exception:
	YOLO_OK = False
	_model = None

CLASSES = ["aphid", "caterpillar", "leaf_spot", "healthy"]


def get_model():
	global _model
	if _model is None and YOLO_OK:
		# For demo, load nano model if available; otherwise simulated
		try:
			_model = YOLO("yolov8n.pt")
		except Exception:
			_model = None
	return _model


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    global _REQS, _ERRS
    _REQS += 1
	img_bytes = await file.read()
	img = Image.open(io.BytesIO(img_bytes)).convert("RGB")

	model = get_model()
	if model is None:
		# Simulated detection: one fake box
		w, h = img.size
		return JSONResponse({
			"model_id": os.getenv("MODEL_ID", "simulated"),
			"detections": [
				{"cls": "aphid", "conf": 0.5, "bbox_xyxy": [int(0.2*w), int(0.2*h), int(0.6*w), int(0.6*h)]}
			],
		})

	# Real prediction path
	res = model.predict(img, verbose=False)
	det_list = []
	for r in res:
		boxes = r.boxes
		if boxes is None:
			continue
		for b in boxes:
			xyxy = b.xyxy[0].tolist()
			cls_idx = int(b.cls.item())
			conf = float(b.conf.item())
			det_list.append({"cls": CLASSES[cls_idx] if cls_idx < len(CLASSES) else str(cls_idx), "conf": conf, "bbox_xyxy": [int(x) for x in xyxy]})
    return JSONResponse({"model_id": os.getenv("MODEL_ID", "yolov8n"), "detections": det_list})


@app.get("/metrics")
def metrics():
    # Minimal counters; integrate with Prometheus client if desired
    return JSONResponse({"requests_total": _REQS, "errors_total": _ERRS})
