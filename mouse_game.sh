#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

source Hand_Tracker/.venv/bin/activate 2>/dev/null || true
python3 Game/game_part.py --input-source mouse
