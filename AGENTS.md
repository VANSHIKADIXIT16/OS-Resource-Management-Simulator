# Project conventions

- Keep the simulator modular: algorithms belong in `modules/`, orchestration in
  `main.py`, and comparisons/report generation in `analysis/`.
- Public algorithm functions validate inputs and return plain dictionaries or
  lists without mutating caller-owned data.
- Keep sample inputs as JSON under `data/`; resolve paths relative to the
  project files, not the current working directory.
- Use only the dependencies declared in `requirements.txt`. Do not install
  packages automatically or modify a global Python installation.
- Log application operations, outcomes, and errors without logging raw user
  input, credentials, or other sensitive values.
- Generated reports belong in `reports/`; screenshots are captured manually
  and saved under `screenshots/`.
- Preserve existing work. Do not discard user changes or commit/push without
  explicit approval.

## Validation

Run the test suite from the project root with:

```bash
python -m pytest -v
```

Regenerate analysis artifacts with:

```bash
python -m analysis.performance
```

Run the menu application with `./run.sh` or `python main.py`. Use the project
virtual environment on macOS and do not silently change Python versions.
