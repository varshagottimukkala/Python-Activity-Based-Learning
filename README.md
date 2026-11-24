# Python Activity-Based Learning

Ten complete solutions selected from **Python Activity1 case studies.pdf**. The brief permits any ten case studies; this selection spans arithmetic, conditions, loops, strings, pattern generation, lists, nested lists, tuples, and unpacking.

**Verification:** 60/60 automated fixtures pass on Python 3.11.2. All ten student programs pass the included syntax-based syllabus checks.

## Start here

- Open [REPORT.html](REPORT.html) locally for the complete illustrated portfolio. It is self-contained, with all diagrams, source code, tests, and output images embedded. Use **Print / Save PDF** for a printable copy.
- On a repository website, use the case-study README links below. Each README contains all ten mandatory deliverables.
- All numeric policies and sample records are explicitly declared classroom assumptions because the supplied brief does not provide rates or thresholds.

## Selected case studies

| Brief case | Study and complete documentation | Main concepts | Tests |
|---|---|---|---|
| 02 | [Progressive Electricity Billing](02_electricity_billing/README.md) | Slabs · conditions · comparisons | 6/6 PASS |
| 13 | [ATM Transaction Sequence Simulation](13_atm_transactions/README.md) | State · validation · reconciliation | 6/6 PASS |
| 14 | [Warehouse Inventory Reconciliation](14_warehouse_reconciliation/README.md) | Lists · arithmetic · discrepancy flags | 6/6 PASS |
| 16 | [Multi-Day Water Tank Simulation](16_water_tank/README.md) | Simulation · loops · conservation | 6/6 PASS |
| 23 | [Student Timetable Conflict Detection](23_timetable_conflicts/README.md) | Strings · tuples · interval overlap | 6/6 PASS |
| 27 | [Advanced Numeric Pattern Generator](27_numeric_diamond/README.md) | Nested loops · symmetry · alignment | 6/6 PASS |
| 29 | [Password Policy Validation Engine](29_password_validation/README.md) | Character scanning · strings · reasons | 6/6 PASS |
| 31 | [String-Based Examination Answer Evaluation](31_answer_evaluation/README.md) | Indexing · negative marking · ties | 6/6 PASS |
| 42 | [Student Marks Matrix Analysis](42_marks_matrix/README.md) | Nested lists · row/column statistics | 6/6 PASS |
| 49 | [Tuple-Based Product Catalogue Audit](49_product_catalogue/README.md) | Tuple unpacking · money · audit | 6/6 PASS |

## Run a program

Requires **Python 3.8 or later**, with no packages to install. From this repository directory:

```bash
python3 02_electricity_billing/program.py
```

Enter the requested values. Each study documents its input contract, retry behavior, and rejection policy. On systems where the executable is named `python`, substitute that command.

Run the included sample without interactive entry:

```bash
python3 02_electricity_billing/program.py < 02_electricity_billing/sample_input.txt
```

Run all verification fixtures:

```bash
python3 tools/run_checks.py
```

The checker validates expected output, rejects unexpected stderr or nonzero exits, enforces a per-test timeout, and checks the student source for out-of-syllabus constructs. It records actual stdout in each case's `test_outputs` folder and writes `verification.json`.

## Mandatory deliverables

Every case directory contains:

| Required material | Location |
|---|---|
| Problem statement, objectives, assumptions | `README.md` |
| Algorithm and computational thinking | `README.md` |
| Flowchart | `assets/flowchart.png`, `assets/flowchart.svg`, `flowchart.mmd` |
| Pseudocode | `README.md` |
| Python source code | `program.py`, also printed in `README.md` |
| Test cases and actual results | `tests.json`, `README.md`, `test_outputs/*.txt` |
| Output screenshot | `assets/output.png` |
| Reproducible sample input and output | `sample_input.txt`, `output.txt` |
| Conclusion | `README.md` |

The output images are rendered PNG captures of actual pseudo-terminal executions of each normal fixture. The plain-text transcripts include the typed fictional inputs. The test stdout files come from separate piped executions, so input text is not echoed in those files.

## Syllabus boundaries

The ten `program.py` files use procedural statements, variables, arithmetic, booleans, conditions, loops, basic input/output and conversions, string operations, lists, nested lists, tuples, and unpacking. They contain no imports, user-defined functions, classes, dictionaries, sets, comprehensions, exception handling, or third-party libraries.

The optional scripts under `tools/` are maintenance utilities, separate from the ten student solutions. They use standard-library features to run tests and generate documents. Rebuilding images also needs ImageMagick and DejaVu fonts; simply running the solutions or reading the finished materials does not.

## Policy and data notes

- The rates and cutoffs are assumed for these classroom exercises, not supplied institutional or commercial policies.
- Codes, transactions, student marks, schedules, and password samples are fictional.
- Each case states whether a malformed record is retried or counted as a rejected attempt.
- Some audit cases reserve a valid identifier before later field validation. This deliberately prevents repeated identifiers from being processed again; the relevant case documents and tests specify the rule.
- The numeric inputs model ordinary classroom-sized records. Scripts expect a complete input sequence; end-of-file recovery is outside the assigned syllabus.

## Repository

[varshagottimukkala/Python-Activity-Based-Learning](https://github.com/varshagottimukkala/Python-Activity-Based-Learning)

**Visibility:** Private.

Give your faculty access to this private repository before submitting its link, or change its visibility if required.

Review and understand the solutions, add your student name, roll number, and section if required, and submit the repository URL according to your faculty's instructions.

## Verification details

See [TEST_REPORT.md](TEST_REPORT.md) for all fixture outcomes and [verification.json](verification.json) for machine-readable results.
