import argparse
import json
from pathlib import Path
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt

from training.metrics import mean_average_precision

CLASSES = ["aphid", "caterpillar", "leaf_spot", "healthy"]


def save_confusion_matrix(y_true, y_pred, labels, out_png: Path):
	cm = confusion_matrix(y_true, y_pred, labels=list(range(len(labels))))
	fig, ax = plt.subplots(figsize=(4,4))
	ax.imshow(cm, cmap="Blues")
	ax.set_xticks(range(len(labels))); ax.set_yticks(range(len(labels)))
	ax.set_xticklabels(labels, rotation=45, ha="right"); ax.set_yticklabels(labels)
	for i in range(cm.shape[0]):
		for j in range(cm.shape[1]):
			ax.text(j, i, cm[i, j], ha="center", va="center", color="black")
	ax.set_xlabel("Predicted"); ax.set_ylabel("True"); ax.set_title("Confusion Matrix")
	fig.tight_layout(); fig.savefig(out_png, dpi=150); plt.close(fig)


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--preds", type=str, required=False)
	parser.add_argument("--out", type=str, default="reports")
	args = parser.parse_args()

	# Placeholder detection metrics (mAP) using simplified function
	preds = [([10,10,100,100], 0, 0.9)]
	gts = [([12,12,98,98], 0)]
	map50 = mean_average_precision(preds, gts, 0.5)

	# Placeholder classification metrics using random labels of size 20
	n = 20
	y_true = np.random.randint(0, len(CLASSES), size=n)
	y_pred = np.random.randint(0, len(CLASSES), size=n)
	report = classification_report(y_true, y_pred, target_names=CLASSES, output_dict=True, zero_division=0)

	out_dir = Path(args.out)
	out_dir.mkdir(parents=True, exist_ok=True)
	save_confusion_matrix(y_true, y_pred, CLASSES, out_dir / "confusion_matrix.png")
	with open(out_dir / "metrics.json", "w", encoding="utf-8") as f:
		json.dump({"mAP@0.5": map50, "classification": report}, f, indent=2)
	(Path(args.out) / "report.html").write_text("<html><body>" +
		f"<h1>Evaluation</h1><p>mAP@0.5: {map50:.3f}</p>" +
		"<img src='confusion_matrix.png' width='400'/>" +
		"</body></html>", encoding="utf-8")
	print("Wrote evaluation report with confusion matrix.")


if __name__ == "__main__":
	main()

