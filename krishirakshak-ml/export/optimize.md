# Optimization Guide

- Quantization: use `export/quantize.py` with `--mode dynamic` or `--mode static` (needs calibration images).
- Pruning: structured/unstructured to reduce weights; retrain to recover accuracy.
- Distillation: train a small student (MobileNet/YOLO-nano) from a larger teacher.
- Benchmark: `python tools/benchmark.py --artifacts artifacts/<model_id>`.

Trade-offs: accuracy vs latency vs size. Always evaluate on a hold-out set and check mobile latency.

