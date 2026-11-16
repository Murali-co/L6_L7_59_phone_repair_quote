# Phone Repair Quote — Labs 6 and 7

**Student:** Murali R · **SRN:** PES2UG25AM805

## Setup and verification

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest LAB6 LAB7 -q
```

Run commands from this repository unless a lab README says otherwise. Both labs
use only Python's standard library at runtime; development dependencies are for tests.

## Deliverables

- `LAB6/PES2UG25AM805_Murali_R_LAB6.pdf`: code and branch coverage report.
- `LAB6/CodeCoverageTest_phone_repair_quote.py`: targeted statement tests.
- `LAB6/BranchCoverageTest_phone_repair_quote.py`: branch and boundary tests.
- `LAB6/evidence/`: recorded coverage output, screenshots and branch coverage JSON.
- `LAB7/PES2UG25AM805_Murali_R_LAB7.pdf`: report following the supplied Lab7.pdf format.
- `LAB7/phone_repair_quote_parser.py`: corrected parsers.
- `LAB7/test_phone_repair_quote_parser.py`: fuzz, property and regression tests.
- `LAB7/evidence/`: before/after execution logs and four report screenshots.

The Lab 7 example report supplies a layout, not the original handout's reflection
questions. The report includes three clearly labelled reflection notes on findings,
defensive fixes and the limits of fuzz testing; these are not quoted handout questions.

Reports can be rebuilt from saved evidence using `python tools/build_reports.py`
after installing `reportlab` and `pillow`. The screenshot step uses headless Chrome.
Before-fix logs are preserved from the original source; rebuilding reports does not
rerun the buggy source or change test results.
