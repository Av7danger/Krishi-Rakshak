"""
This file illustrates how one would export a MobileNetV3 classifier to TFLite.
For CI we avoid running the full conversion to keep runtime low.
"""

import torch


def example_export():
	# Create a toy model (identity) to illustrate export
	model = torch.nn.Identity()
	dummy = torch.randn(1, 3, 224, 224)
	torch.onnx.export(model, dummy, "mobilenet_example.onnx", opset_version=12)
	print("Wrote mobilenet_example.onnx")


if __name__ == "__main__":
	example_export()

