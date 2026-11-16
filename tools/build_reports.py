"""Build student reports and browser screenshots from recorded terminal evidence."""
from pathlib import Path
from html import escape
from importlib.metadata import version
import re
import subprocess
import tempfile
import textwrap

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
NAVY = colors.HexColor('#183454')
TEAL = colors.HexColor('#24647e')
LIGHT = colors.HexColor('#eaf1f5')
BORDER = colors.HexColor('#bed0df')
W, H = 595.28, 841.89
M = 51
CONTENT = W - 2 * M
BODY = ParagraphStyle('body', fontName='Helvetica', fontSize=9.4, leading=13.5)
SMALL = ParagraphStyle('small', parent=BODY, fontSize=8.1, leading=11)
CAPTION = ParagraphStyle('caption', parent=SMALL, textColor=colors.HexColor('#50647b'), alignment=TA_CENTER)


def capture(folder, stem, title, excerpt=False):
    evidence = ROOT / folder / 'evidence'
    content = (evidence / (stem + '.txt')).read_text()
    if excerpt:
        lines = content.splitlines()
        selected = [line for line in lines if (
            line.startswith('$ ') or 'collected ' in line or
            ('::test_' in line and ('FAILED' in line or 'PASSED' in line)) or
            line.startswith('E   Failed:') or ' distinct failures.' in line or
            line.startswith('    | Failed:') or
            re.search(r'\d+ (?:failed|passed),', line)
        )]
        content = '\n'.join(selected)
    wrapped = []
    for line in content.splitlines():
        wrapped.extend(textwrap.wrap(line, width=112, replace_whitespace=False,
                                     drop_whitespace=False) or [''])
    html = f'''<!doctype html><meta charset="utf-8"><style>
    *{{box-sizing:border-box}}body{{margin:0;background:#111827;color:#e5edf8;padding:25px}}
    header{{font:20px sans-serif;color:#90c8f5;border-bottom:1px solid #35435a;padding-bottom:15px;margin-bottom:18px}}
    pre{{font:18px/1.45 'DejaVu Sans Mono',monospace;margin:0;white-space:pre-wrap}}
    </style><header>{escape(title)} | Captured terminal output{' (excerpt)' if excerpt else ''}</header><pre>{escape(chr(10).join(wrapped))}</pre>'''
    height = 125 + len(wrapped) * 27
    target = evidence / (stem + '.png')
    with tempfile.TemporaryDirectory(prefix='phone-repair-capture-') as tmp:
        page = Path(tmp) / 'output.html'
        page.write_text(html)
        result = subprocess.run([
            'google-chrome', '--headless', '--no-sandbox', '--disable-gpu',
            '--disable-dev-shm-usage', '--hide-scrollbars',
            '--no-first-run', '--disable-background-networking',
            f'--user-data-dir={tmp}/profile', f'--screenshot={target}',
            f'--window-size=1400,{height}', page.as_uri(),
        ], capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise RuntimeError(result.stderr)
    with Image.open(target) as image:
        image.verify()
    return target


class Report:
    def __init__(self, path, lab):
        self.c = canvas.Canvas(str(path), pagesize=(W, H))
        self.c.setTitle(f'Lab {lab} Report - Murali R - PES2UG25AM805')
        self.c.setAuthor('Murali R')
        self.lab = lab
        self.page = 0
        self.y = H - 44
        self.new_page(first=True)

    def new_page(self, first=False):
        if not first:
            self.footer()
            self.c.showPage()
        self.page += 1
        self.y = H - 44

    def footer(self):
        self.c.setStrokeColor(BORDER)
        self.c.line(M, 37, W-M, 37)
        self.c.setFillColor(colors.HexColor('#59738d'))
        self.c.setFont('Helvetica', 7.6)
        topic = 'Fuzzing for Input Validation Bugs' if self.lab == 7 else 'Code and Branch Coverage'
        self.c.drawString(M, 24, f'Lab {self.lab} - {topic}')
        self.c.drawRightString(W-M, 24, f'Page {self.page}')

    def text(self, value, style=BODY, gap=7):
        para = Paragraph(value, style)
        _, height = para.wrap(CONTENT, 1000)
        if self.y - height < 52:
            raise ValueError(f'Content overflows page {self.page}: {value[:60]}')
        para.drawOn(self.c, M, self.y-height)
        self.y -= height + gap

    def heading(self, value, size=14):
        style = ParagraphStyle('heading', parent=BODY, fontName='Helvetica-Bold',
                               fontSize=size, leading=size+3, textColor=NAVY)
        self.text(value, style, gap=6)

    def sub(self, value):
        self.text(value, ParagraphStyle('sub', parent=BODY, fontName='Helvetica-Bold',
                                       fontSize=11.2, leading=14, textColor=TEAL), gap=5)

    def table(self, rows, widths, header=False):
        rows = [[Paragraph(str(cell), SMALL) for cell in row] for row in rows]
        table = Table(rows, colWidths=widths, hAlign='LEFT')
        commands = [
            ('GRID', (0, 0), (-1, -1), .5, BORDER),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]
        if header:
            commands += [('BACKGROUND', (0, 0), (-1, 0), LIGHT)]
        else:
            commands += [('BACKGROUND', (0, 0), (0, -1), LIGHT)]
        table.setStyle(TableStyle(commands))
        _, height = table.wrap(CONTENT, 1000)
        if self.y-height < 52:
            raise ValueError(f'Table overflows page {self.page}')
        table.drawOn(self.c, M, self.y-height)
        self.y -= height + 11

    def figure(self, path, caption, max_height=220):
        with Image.open(path) as picture:
            width, height = picture.size
        scale = min(CONTENT/width, max_height/height)
        width, height = width*scale, height*scale
        if self.y-height < 75:
            raise ValueError(f'Figure overflows page {self.page}')
        self.c.drawImage(ImageReader(str(path)), M+(CONTENT-width)/2, self.y-height,
                         width=width, height=height)
        self.y -= height + 7
        self.text(caption, CAPTION, gap=12)

    def cover(self, title, application):
        self.y = H - 60
        title_style = ParagraphStyle('title', parent=BODY, fontName='Helvetica-Bold',
                                    fontSize=22, leading=28, alignment=TA_CENTER, textColor=NAVY)
        self.text(f'LAB {self.lab}', title_style, gap=10)
        self.text(title, ParagraphStyle('title2', parent=title_style, fontSize=20, leading=25), gap=10)
        self.text(application + ' Application', ParagraphStyle('subtitle', parent=BODY,
                  alignment=TA_CENTER, fontSize=11, textColor=TEAL), gap=14)
        self.c.setStrokeColor(TEAL)
        self.c.line(M+60, self.y, W-M-60, self.y)
        self.y -= 28
        self.table([
            ['<b>Student Name</b>', 'Murali R'],
            ['<b>SRN</b>', 'PES2UG25AM805'],
            ['<b>Course / Section</b>', 'Software Engineering'],
            ['<b>Assigned Application</b>', application],
            ['<b>Tools Used</b>', 'Python 3.12.3, Hypothesis, Pytest, Coverage.py'],
        ], [140, CONTENT-140])

    def save(self):
        self.footer()
        self.c.save()


def lab7(images):
    report = Report(ROOT/'LAB7/PES2UG25AM805_Murali_R_LAB7.pdf', 7)
    report.cover('Fuzzing for Input Validation Bugs', 'Phone Repair Quote Parser')
    report.sub('Experiment objective')
    report.text('Explore fuzz testing as a quality-assurance technique by using Hypothesis to discover input-validation bugs, harden the phone-repair parsers, and verify the fixes using Pytest.')
    report.y -= 14
    report.sub('Submission contents')
    report.text('This report documents the original application run, fuzz-testing failures, defensive code changes and the final successful test run. Corrected application and test source files are submitted separately.')
    report.heading('1. Introduction')
    report.text('Fuzz testing exercises programs with unexpected, malformed and edge-case inputs. Property-based testing generates many examples automatically, while Hypothesis shrinks a failure to a small reproducible input.')
    report.text('The <font face="Courier">@given</font> decorator and <font face="Courier">st.text() | st.none()</font> generate arbitrary Unicode strings and missing values. Pytest discovers the tests and reports any unexpected exception.')

    report.new_page()
    report.heading('2. Software Requirements and Setup')
    report.text(f'Python 3.12.3; Hypothesis {version("hypothesis")}; Pytest {version("pytest")}; Coverage.py {version("coverage")}. Tests were executed on Linux in an isolated virtual environment.')
    report.text('<font face="Courier">python -m venv .venv<br/>source .venv/bin/activate<br/>python -m pip install -r requirements-dev.txt</font>')
    report.heading('3. Functions Under Test')
    report.text('<b>mask_imei(imei):</b> removes dashes and whitespace, then hides all but the last four ASCII digits. Example: 35-209900-176148-1 becomes ***********1481.')
    report.text('<b>parse_parts_order(text):</b> converts semicolon-separated part/quantity items into a dictionary. Example: screen x1; battery x2 becomes {"screen": 1, "battery": 2}.')
    report.text('<b>parse_model(text):</b> separates the brand from a possibly multiword model. Example: Samsung Galaxy S23 becomes ("Samsung", "Galaxy S23").')
    report.heading('4. Test Design')
    report.text('Three required Hypothesis tests call the corresponding parser inside a try/except block and fail if an exception occurs. Each uses up to 200 examples from arbitrary text or None. Deterministic generation makes the demonstrations reproducible; returned types are also checked.')
    report.text('Additional regression cases cover valid samples, empty and non-string inputs, Unicode whitespace, malformed quantities, huge integers, duplicate parts and brand-only model names. Two further properties check masking and preservation of generated valid order quantities. The complete Lab 7 suite has 40 test cases.')
    report.heading('5. Procedure and Observations')
    report.sub('Step 1 - Run the original application')
    report.text('The original application was executed using the three valid sample inputs. All expected outputs were produced. This successful run does not exercise missing or malformed values; SS1 appears on the next page.')
    report.text('Evidence note: figures are browser screenshots of saved terminal logs. SS2 shows an excerpt to keep the failures readable; complete unedited output is retained in the evidence folder.', SMALL)

    report.new_page()
    report.figure(images['SS1_original_cli'], 'Figure 1 / SS1. Original parser executed with valid sample inputs.', 235)
    report.sub('Step 2 - Run Hypothesis tests against the original code')
    report.text('The required tests were run before changing the parser:<br/><font face="Courier">python -m pytest test_phone_repair_quote_parser.py<br/>-k no_crash -v --tb=short --color=no</font>')
    report.figure(images['SS2_original_fuzz'], 'Figure 2 / SS2. All three original functions fail the no-crash property.', 195)
    report.sub('Observed failures')
    report.table([
        ['<b>Function</b>', '<b>Discovered input</b>', '<b>Observed exception</b>'],
        ['mask_imei', 'None', 'AttributeError: replace called on None'],
        ['parse_parts_order', 'None, empty string, "x"', 'AttributeError / ValueError'],
        ['parse_model', 'None, empty string', 'AttributeError / ValueError'],
    ], [114, 145, CONTENT-259], header=True)

    report.new_page()
    report.heading('6. Bug Fixes and Defensive Programming')
    report.text('<b>mask_imei:</b> checks the input type, removes whitespace/dashes and checks ASCII digits before masking. Invalid or non-string values return an empty string. The last-four rule remains unchanged; IMEI checksum validation is outside this helper.')
    report.text('<b>parse_parts_order:</b> checks the input type, validates each entry with a full regex match, catches oversized integer conversions, skips invalid/non-positive quantities and sums repeated parts. Valid entries survive a malformed item; non-string input returns an empty dictionary.')
    report.text('<b>parse_model:</b> checks the input type, splits on any whitespace once and checks the field count. Empty or non-string input returns ("", ""); a single brand returns (brand, ""). Multiword model names are preserved.')
    report.sub('Step 3 - Execute the corrected application')
    report.figure(images['SS3_fixed_cli'], 'Figure 3 / SS3. Corrected application preserves valid sample outputs.', 200)
    report.heading('7. Final Verification')
    report.text('The same three required fuzz tests were rerun against the corrected source. Each passed. The additional full suite also passed: <b>40 tests passed</b>.')
    report.figure(images['SS4_fixed_fuzz'], 'Figure 4 / SS4. All three required Hypothesis tests pass after the fixes.', 180)

    report.new_page()
    report.heading('8. Result and Conclusion')
    report.text('Hypothesis exposed input-validation weaknesses in all three original parsers. Missing values triggered AttributeError; empty or malformed strings triggered unpacking and integer-conversion ValueError exceptions. The minimized examples made each bug easy to reproduce.')
    report.text('Type checks, format validation, safe splitting and targeted exception handling now prevent those crashes. Original valid examples still produce the same outputs. The required fuzz tests pass, and all 40 Lab 7 test cases pass.')
    report.sub('Reflection notes')
    report.text('<b>1. What did fuzzing uncover?</b> The original functions assumed every input was a correctly formatted string. None, an empty string and "x" were sufficient to expose these assumptions.')
    report.text('<b>2. How were the fixes chosen?</b> Each function has a documented empty-result policy. Validation happens before string operations and conversion, while valid user data is preserved. Mixed orders keep valid entries instead of losing the entire order.')
    report.text('<b>3. What are the limits of the evidence?</b> Finite fuzzing cannot prove correctness for every input or guarantee business-rule accuracy. No-crash checks are supplemented with expected-output regressions and properties. The IMEI helper masks digits; it does not certify a real IMEI.')
    report.text('These notes summarize the experiment. The supplied sample PDF does not contain the original handout\'s three reflection prompts.', SMALL)
    report.heading('9. Files to Submit')
    report.text('1. PES2UG25AM805_Murali_R_LAB7.pdf - report and four figures.<br/>2. phone_repair_quote_parser.py - corrected application.<br/>3. test_phone_repair_quote_parser.py - completed Hypothesis and regression tests.<br/>4. evidence/ - supporting logs and image captures.')
    report.y -= 22
    report.text('End of Report', CAPTION)
    report.save()


def lab6(images):
    report = Report(ROOT/'LAB6/PES2UG25AM805_Murali_R_LAB6.pdf', 6)
    report.cover('Code and Branch Coverage Analysis', 'Phone Repair Quote')
    report.sub('Experiment objective')
    report.text('Measure statement and branch coverage, identify untested decisions, and write tests that achieve the handout\'s minimum 90% requirement. The final application achieves <b>100% statement coverage and 100% measured branch coverage</b>.')
    report.heading('1. Application and Test Design')
    report.text('<b>repair_quote:</b> test all four parts, both brand tiers, warranty states and express states, plus invalid part and tier errors. Warranty removes the non-screen part cost while labour and express charges remain payable.')
    report.text('<b>repair_days:</b> test available/unavailable stock, zero and positive technician counts, and the five-day versus two-day restocking delays.')
    report.text('<b>trade_in_value:</b> test the 12/13, 24/25 and 48/49 month boundaries, cracked-screen discounts, integer rounding and invalid input exceptions.')
    report.heading('2. Test Files')
    report.text('<font face="Courier">CodeCoverageTest_phone_repair_quote.py</font>: 14 targeted cases execute every application statement.<br/><font face="Courier">BranchCoverageTest_phone_repair_quote.py</font>: 76 cases exercise decision outcomes and boundary behaviour.<br/><font face="Courier">test_phone_repair_quote.py</font>: default Pytest entry point collecting both suites.')
    report.text('The application source required no changes. Coverage is restricted to phone_repair_quote.py; test code is excluded from application coverage.')

    report.new_page()
    report.heading('3. Code Coverage Analysis')
    report.text('From LAB6, after activating the project virtual environment:')
    report.text('<font face="Courier">python -m coverage run --source=phone_repair_quote<br/>-m pytest CodeCoverageTest_phone_repair_quote.py -q<br/>python -m coverage report -m --fail-under=100</font>')
    report.figure(images['line_coverage'], 'Figure 1. Final line coverage output, after exceeding the 90% requirement.', 260)
    report.table([
        ['<b>Metric</b>', '<b>Observed value</b>'],
        ['Test cases passed', '14'], ['Application statements', '40'],
        ['Statements missed', '0'], ['Statement coverage', '100%'],
    ], [CONTENT/2, CONTENT/2], header=True)
    report.sub('Interpretation')
    report.text('Every measured statement executes at least once. This includes the exception statements for invalid part, brand tier, price and age, as well as all three depreciation rates and the expired trade-in return.')
    report.text('Statement coverage alone does not establish that every decision outcome or condition combination has been checked. The separate branch suite broadens the inputs and verifies boundaries with expected outputs.')

    report.new_page()
    report.heading('4. Branch Coverage Analysis')
    report.text('<font face="Courier">python -m coverage run --branch --source=phone_repair_quote<br/>-m pytest BranchCoverageTest_phone_repair_quote.py -q<br/>python -m coverage report -m --fail-under=100</font>')
    report.figure(images['branch_coverage'], 'Figure 2. Final branch coverage: 28 branches, zero partial branches.', 270)
    report.table([
        ['<b>Metric</b>', '<b>Observed value</b>'],
        ['Test cases passed', '76'], ['Statements / missed', '40 / 0'],
        ['Measured branches / covered', '28 / 28'],
        ['Partial / missing branches', '0 / 0'], ['Combined coverage', '100%'],
    ], [CONTENT/2, CONTENT/2], header=True)
    report.heading('5. Result and Conclusion')
    report.text('Both suites pass and exceed the handout\'s 90% threshold. The branch suite tests both outcomes of the measured decisions and checks business outputs across valid combinations and age boundaries. Full measured coverage does not prove that every possible execution path or input has been tested.')
    report.text('Deliverables: this report, both named test suites, the default test entry point, evidence images/logs and the machine-readable branch coverage JSON. The local history includes separate code-coverage and branch-coverage commits.')
    report.save()


def main():
    images7 = {}
    for stem, title in [
        ('SS1_original_cli', 'SS1 - Original application'),
        ('SS2_original_fuzz', 'SS2 - Fuzzing the original application'),
        ('SS3_fixed_cli', 'SS3 - Corrected application'),
        ('SS4_fixed_fuzz', 'SS4 - Fuzzing the corrected application'),
    ]:
        images7[stem] = capture('LAB7', stem, title, excerpt=stem=='SS2_original_fuzz')
    images6 = {}
    for stem, title in [('line_coverage', 'Lab 6 - Statement coverage'),
                        ('branch_coverage', 'Lab 6 - Branch coverage')]:
        images6[stem] = capture('LAB6', stem, title)
    lab7(images7)
    lab6(images6)
    print('Built both reports and six evidence screenshots.')


if __name__ == '__main__':
    main()
