"""Default pytest entry point for both handout test suites."""

from CodeCoverageTest_phone_repair_quote import (
    test_line_quote, test_line_invalid_quote, test_line_days,
    test_line_trade_in, test_line_invalid_trade_in,
)
from BranchCoverageTest_phone_repair_quote import (
    test_repair_quote, test_invalid_quote, test_repair_days,
    test_trade_in_age_boundaries, test_invalid_trade_in, test_trade_in_rounds_down,
)
