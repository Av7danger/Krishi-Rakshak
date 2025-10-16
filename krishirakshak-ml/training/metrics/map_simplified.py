from typing import List, Tuple


def iou(boxA, boxB) -> float:
	# boxes as [x1,y1,x2,y2]
	xA = max(boxA[0], boxB[0])
	yA = max(boxA[1], boxB[1])
	xB = min(boxA[2], boxB[2])
	yB = min(boxA[3], boxB[3])
	inter = max(0, xB - xA) * max(0, yB - yA)
	areaA = max(0, boxA[2]-boxA[0]) * max(0, boxA[3]-boxA[1])
	areaB = max(0, boxB[2]-boxB[0]) * max(0, boxB[3]-boxB[1])
	union = areaA + areaB - inter + 1e-9
	return inter / union


def mean_average_precision(preds: List[Tuple[List[int], int, float]], gts: List[Tuple[List[int], int]], iou_thr: float = 0.5) -> float:
	"""Simplified mAP@0.5 over a flat list of detections.
	preds: list of (bbox, cls, conf)
	gts: list of (bbox, cls)
	"""
	if not preds or not gts:
		return 0.0
	preds = sorted(preds, key=lambda x: x[2], reverse=True)
	used = [False] * len(gts)
	tp, fp = 0, 0
	for pb, pc, pcfg in preds:
		match = -1
		best_iou = 0.0
		for i, (gb, gc) in enumerate(gts):
			if used[i] or pc != gc:
				continue
			iou_v = iou(pb, gb)
			if iou_v > iou_thr and iou_v > best_iou:
				best_iou = iou_v
				match = i
		if match >= 0:
			used[match] = True
			tp += 1
		else:
			fp += 1
	prec = tp / max(1, tp + fp)
	recall = tp / max(1, len(gts))
	return (prec + recall) / 2.0

