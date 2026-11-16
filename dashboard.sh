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
    echo "Python 3 was not found. Create a project virtual environment first."
    exit 1
fi

if ! "$PYTHON" -c 'import streamlit, pandas, matplotlib' >/dev/null 2>&1; then
    echo "Dashboard dependencies are missing. Run:"
    echo "  $PYTHON -m pip install -r requirements.txt"
    exit 1
fi

exec "$PYTHON" -m streamlit run "$PROJECT_ROOT/dashboard.py" "$@"
