from fastapi.testclient import TestClient
from krishirakshak_ml.inference.serve.app import app
from PIL import Image
import numpy as np
import io


def test_predict():
	client = TestClient(app)
	img = Image.fromarray((np.random.rand(64,64,3)*255).astype('uint8'))
	buf = io.BytesIO()
	img.save(buf, format='PNG')
	buf.seek(0)
	r = client.post('/predict', files={'file': ('x.png', buf, 'image/png')})
	assert r.status_code == 200
	data = r.json()
	assert 'model_id' in data and 'detections' in data

