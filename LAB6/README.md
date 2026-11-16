# L6_L7_59 — Phone Repair Quote

Lab 6: Code and Branch Coverage

## About

A small Python module that quotes phone repairs by part, brand tier, warranty and express service, estimates turnaround time and values phones offered for trade-in.

## Files

| File | Description |
|------|-------------|
| `phone_repair_quote.py` | The module under test |
| `test_phone_repair_quote.py` | Default pytest entry point for both suites |
| `CodeCoverageTest_phone_repair_quote.py` | 14 targeted line coverage cases |
| `BranchCoverageTest_phone_repair_quote.py` | 76 branch and boundary cases |
| `PES2UG25AM805_Murali_R_LAB6.pdf` | Report with coverage screenshots |

## Run from this folder after activating the repository virtual environment

```bash
python -m coverage run --source=phone_repair_quote -m pytest CodeCoverageTest_phone_repair_quote.py -q
python -m coverage report -m --fail-under=100
python -m coverage run --branch --source=phone_repair_quote -m pytest BranchCoverageTest_phone_repair_quote.py -q
python -m coverage report -m --fail-under=100
python -m coverage html
```

Both suites achieve 100% statement coverage. The branch suite covers all 28
measured branches with zero partial branches. Only the application is measured.
`evidence/` contains output and screenshots; `htmlcov/index.html` can be regenerated.
