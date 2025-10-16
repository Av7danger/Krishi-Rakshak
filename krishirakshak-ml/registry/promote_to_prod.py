import argparse
import json
from pathlib import Path
from datetime import datetime

IDX = Path("krishirakshak-ml/registry/store/index.json")


def bump_version(prev: str, major: bool = False, minor: bool = False) -> str:
	if not prev or prev[0] != 'v':
		return 'v1.0.0'
	M, m, p = map(int, prev[1:].split('.'))
	if major:
		return f"v{M+1}.0.0"
	if minor:
		return f"v{M}.{m+1}.0"
	return f"v{M}.{m}.{p+1}"


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--model-id', type=str, required=True)
	parser.add_argument('--bump', choices=['patch','minor','major'], default='patch')
	args = parser.parse_args()

	idx = json.loads(IDX.read_text(encoding='utf-8')) if IDX.exists() else {'models': []}
	entry = next((e for e in idx['models'] if e['id'] == args.model_id), None)
	if not entry:
		raise SystemExit('Model not found in registry')
	card_p = Path(entry['path']) / 'model_card.json'
	card = json.loads(card_p.read_text(encoding='utf-8'))
	prev = card.get('version', 'v0.0.0')
	version = bump_version(prev, major=args.bump=='major', minor=args.bump=='minor')
	card['version'] = version
	card['date'] = datetime.utcnow().isoformat() + 'Z'
	card_p.write_text(json.dumps(card, indent=2), encoding='utf-8')
	(Path('krishirakshak-ml/registry/store/latest')).write_text(args.model_id, encoding='utf-8')
	print(f"Promoted {args.model_id} -> {version}")


if __name__ == '__main__':
	main()
