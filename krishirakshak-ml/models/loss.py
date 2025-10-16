import torch
import torch.nn as nn


class FocalLoss(nn.Module):
	def __init__(self, gamma: float = 2.0, alpha: float = 0.25):
		super().__init__()
		self.gamma = gamma
		self.alpha = alpha

	def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
		bce = nn.functional.binary_cross_entropy_with_logits(logits, targets, reduction="none")
		prob = torch.sigmoid(logits)
		pt = torch.where(targets == 1, prob, 1 - prob)
		loss = self.alpha * (1 - pt) ** self.gamma * bce
		return loss.mean()

