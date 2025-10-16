#!/usr/bin/env bash
set -euo pipefail
ROOT="krishirakshak-ml"
REG="$ROOT/registry/store"
LATEST=$(cat "$REG/latest" 2>/dev/null || echo "")
if [ -z "$LATEST" ]; then
	echo "No latest model found" >&2
	exit 1
fi
SRC="$ROOT/artifacts/$LATEST"
DST="$ROOT/inference/serve/model"
mkdir -p "$DST"
cp -r "$SRC"/* "$DST"/
echo "Copied $LATEST to $DST"
