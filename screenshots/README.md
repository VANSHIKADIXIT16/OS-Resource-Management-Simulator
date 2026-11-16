# Manual screenshot checklist

Capture genuine screenshots in VS Code or Terminal and save them in this
directory. Do not use generated charts as application screenshots.

Suggested captures:

1. `01-main-menu.png` — launch `./run.sh` and show the main menu.
2. `02-cpu-comparison.png` — choose CPU scheduling, then compare all; include
   the Gantt timelines and averages.
3. `03-memory-comparison.png` — compare the three allocation strategies and
   show fragmentation separately from free memory.
4. `04-deadlock-safe-sequence.png` — run the sample Banker check.
5. `05-disk-comparison.png` — compare FCFS, SSTF, and SCAN including movement.
6. `06-reports-folder.png` — show generated CSVs, charts, and sample trace.
7. `07-tests-passing.png` — show `python -m pytest -v` ending in its pass
   summary.

For terminal captures, use the project root and the activated project
environment. Avoid capturing personal paths, credentials, or unrelated
terminal content.
