# L6_L7_59 — Phone Repair Quote

Lab 7: Fuzzing for Input Validation Bugs

## About

A small Python module that reads phone repair quote details typed in by a user:
IMEI numbers, parts orders and phone models. The corrected parsers handle missing
and malformed input without raising exceptions.

## Files

| File | Description |
|------|-------------|
| `phone_repair_quote_parser.py` | Corrected parsing module |
| `test_phone_repair_quote_parser.py` | Three required fuzz tests plus regression/property tests |
| `PES2UG25AM805_Murali_R_LAB7.pdf` | Completed report using the supplied sample layout |

Keep all your Lab 7 work in this `LAB7` folder.

Follow the lab handout for the full instructions. Use the file names above wherever the handout refers to the code and test files.

## Screenshots

| Screenshot | What it must show |
|------------|-------------------|
| SS1 | `python phone_repair_quote_parser.py` run on the buggy module |
| SS2 | `pytest test_phone_repair_quote_parser.py` with your completed tests failing on the buggy module |
| SS3 | `python phone_repair_quote_parser.py` run on your fixed module |
| SS4 | `pytest test_phone_repair_quote_parser.py` with all tests passing on your fixed module |

## Deliverables

Commit these three files in this `LAB7` folder:

1. `phone_repair_quote_parser.py`: your fixed module. All three functions must handle any input without crashing.
2. `test_phone_repair_quote_parser.py`: your completed Hypothesis tests, one for each of the three functions.
3. `PES2UG25AM805_Murali_R_LAB7.pdf`: figures SS1 to SS4 and three reflection notes.

Be ready to explain the bugs you found and how you fixed them. You may be called on to present.

## Run from this folder after activating the repository virtual environment

```bash
python phone_repair_quote_parser.py
python -m pytest test_phone_repair_quote_parser.py -k no_crash -v
python -m pytest test_phone_repair_quote_parser.py -q
```

The three required fuzz tests each generate up to 200 examples of arbitrary text
or `None`; all 40 test cases pass. `evidence/SS2_original_fuzz.txt` records the
failures observed before fixing the source. Figures are screenshots of saved
terminal output rendered in a browser; the complete text logs are retained.

## Input handling policy

- `mask_imei`: removes dashes and whitespace, requires ASCII digits, and masks all
  but the last four. Empty, invalid and non-string inputs return `""`. At most four
  digits are returned unchanged. This is masking, not IMEI checksum validation.
- `parse_parts_order`: accepts positive ASCII integer quantities separated from a
  non-empty part by `x` or `X`. Skips invalid entries, preserves valid entries,
  sums duplicate part quantities, and returns `{}` for non-string input. Part
  names are case-sensitive; the parser does not enforce a repair-parts catalogue.
- `parse_model`: accepts whitespace separators and preserves multiword model
  names. A single word becomes `(brand, "")`; empty/non-string input returns
  `("", "")`.
