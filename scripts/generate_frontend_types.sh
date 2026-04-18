#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_FILE="$ROOT_DIR/frontend/types/generated-api.ts"
TMP_SCHEMA="$(mktemp)"

curl -sSf "${API_BASE_URL:-http://localhost:8000}/openapi.json" > "$TMP_SCHEMA"
npx openapi-typescript "$TMP_SCHEMA" --output "$OUTPUT_FILE"
rm -f "$TMP_SCHEMA"

echo "Generated $OUTPUT_FILE"
