"""
Tests for src/utils/date_utils.py
"""
import pytest
from src.utils.date_utils import parse_expense_date


class TestParseExpenseDate:
    def test_yyyy_mm_dd(self):
        assert parse_expense_date("2026-05-15") == "2026-05-15"

    def test_mm_dd_yy(self):
        assert parse_expense_date("05/15/26") == "2026-05-15"

    def test_mm_dd_yyyy(self):
        assert parse_expense_date("05/15/2026") == "2026-05-15"

    def test_yyyy_slash_mm_slash_dd(self):
        assert parse_expense_date("2026/05/15") == "2026-05-15"

    def test_two_digit_year_century_boundary(self):
        """Python strptime maps 00-68 → 2000-2068, 69-99 → 1969-1999."""
        assert parse_expense_date("01/01/26") == "2026-01-01"
        assert parse_expense_date("01/01/68") == "2068-01-01"
        assert parse_expense_date("01/01/69") == "1969-01-01"
        assert parse_expense_date("01/01/99") == "1999-01-01"

    def test_invalid_date_raises(self):
        with pytest.raises(ValueError):
            parse_expense_date("not-a-date")

    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            parse_expense_date("")
