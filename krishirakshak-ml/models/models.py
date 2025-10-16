from dataclasses import dataclass
from typing import Any, List

try:
	from ultralytics import YOLO
	ULTRA = True
except Exception:
	ULTRA = False

try:
	import timm
	import torch
	import torch.nn as nn
	TIMM = True
except Exception:
	TIMM = False
	class nn:  # type: ignore
		Module = object


@dataclass
class Prediction:
	boxes: List[List[int]]
	classes: List[str]
	confs: List[float]


class DetectionModel:
	"""Thin wrapper around ultralytics YOLO to allow pluggability."""
	def __init__(self, weights: str = "yolov8n.pt") -> None:
		self.available = ULTRA
		self.classes = ["aphid", "caterpillar", "leaf_spot", "healthy"]
		self.model = YOLO(weights) if ULTRA else None

	def predict(self, image) -> Prediction:
		if not self.model:
			# Simulated single box
			return Prediction(boxes=[[10, 10, 100, 100]], classes=["aphid"], confs=[0.5])
		res = self.model.predict(image, verbose=False)
		boxes, clss, confs = [], [], []
		for r in res:
			if r.boxes is None:
				continue
			for b in r.boxes:
				boxes.append([int(x) for x in b.xyxy[0].tolist()])
				clss.append(self.classes[int(b.cls.item())] if int(b.cls.item()) < len(self.classes) else str(int(b.cls.item())))
				confs.append(float(b.conf.item()))
		return Prediction(boxes=boxes, classes=clss, confs=confs)


class MobileClassifier(nn.Module):
	"""MobileNetV3-small based classifier for healthy vs diseased as fallback."""
	def __init__(self, num_classes: int = 2):
		super().__init__()
		if not TIMM:
			self.backbone = None
			self.head = None
			return
		self.backbone = timm.create_model("mobilenetv3_small_100", pretrained=True, num_classes=num_classes)

	def forward(self, x: Any):  # type: ignore
		if self.backbone is None:
			return x
		return self.backbone(x)

