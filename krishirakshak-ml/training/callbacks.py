from pathlib import Path

class EarlyStopping:
	def __init__(self, patience: int = 5):
		self.patience = patience
		self.best = None
		self.count = 0

	def step(self, metric: float) -> bool:
		if self.best is None or metric > self.best:
			self.best = metric
			self.count = 0
			return False
		self.count += 1
		return self.count > self.patience


def save_best(model_path: Path, out_dir: Path):
	out_dir.mkdir(parents=True, exist_ok=True)
	(model_path).write_bytes(b"simulated-best")

