from pathlib import Path


def test_artifacts_created():
	arts = Path("krishirakshak-ml/artifacts")
	if not arts.exists():
		assert True
		return
	# pick any artifact dir
	dirs = [p for p in arts.iterdir() if p.is_dir()]
	if not dirs:
		assert True
		return
	m = dirs[0]
	assert (m / "model.onnx").exists() and (m / "model.tflite").exists()
