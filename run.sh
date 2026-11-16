#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

if [[ -x "$PROJECT_ROOT/venv/bin/python" ]]; then
    PYTHON="$PROJECT_ROOT/venv/bin/python"
elif [[ -x "$PROJECT_ROOT/.venv/bin/python" ]]; then
    PYTHON="$PROJECT_ROOT/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON="$(command -v python3)"
else
    printf '%s\n' "Python 3 was not found. Install Python 3 and create a project venv."
    exit 1
fi

if ! "$PYTHON" -c 'import sys; raise SystemExit(sys.version_info.major != 3)'; then
    printf '%s\n' "The selected interpreter is not Python 3: $PYTHON"
    exit 1
fi

if ! "$PYTHON" -c 'import pandas, matplotlib' >/dev/null 2>&1; then
    printf '%s\n' \
        "Project dependencies are missing for $PYTHON." \
        "Activate a project virtual environment and install them with:" \
        "  python -m pip install -r requirements.txt"
    exit 1
fi

exec "$PYTHON" "$PROJECT_ROOT/main.py"
