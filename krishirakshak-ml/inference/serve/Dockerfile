FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install -U pip && pip install -e . && pip install uvicorn
ENV MODEL_ID=simulated
EXPOSE 8000
CMD ["uvicorn", "krishirakshak_ml.inference.serve.app:app", "--host", "0.0.0.0", "--port", "8000"]

