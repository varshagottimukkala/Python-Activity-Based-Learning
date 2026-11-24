# Optional maintenance utilities

These utilities are separate from the ten introductory student programs.

## Verify solutions

From the repository root:

```bash
python3 tools/run_checks.py
```

Only the Python standard library is needed. The checker executes all 60 input fixtures, compares the expected result strings, checks for unwanted output, and validates syllabus restrictions in the ten `program.py` files.

## Rebuild documents and images

```bash
python3 tools/build_materials.py
```

Run verification first. Rebuilding uses `study_notes.json`, each program, its fixtures, and the verification results. It requires a Unix-like system with Python, pseudo-terminal support, the ImageMagick `convert` command, and the DejaVu Sans / Sans Mono fonts. It captures a normal run of every program, renders the flowcharts and transcript images, and generates the case READMEs, root README, test report, and self-contained HTML report.

Generated documentation is derived from `study_notes.json` and the current source files. Update those inputs and rerun the tools when changing a policy.
