import argparse
import time


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--duration", type=float, default=0.02)
	args = parser.parse_args()
	start = time.time(); time.sleep(args.duration); print(f"Profiled for {time.time()-start:.3f}s")


if __name__ == "__main__":
	main()

