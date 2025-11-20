#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# Activate the hand-tracker venv
source Hand_Tracker/.venv/bin/activate 2>/dev/null || true

python3 Hand_Tracker/hand_tracker.py &
tracker_pid=$!

python3 Game/game_part.py --input-source hand_tracking

kill "$tracker_pid" 2>/dev/null || true
