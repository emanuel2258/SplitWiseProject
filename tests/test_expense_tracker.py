"""
Tests for src/core/expense_tracker.py
"""
import pytest
from src.core.expense_tracker import expense_should_count_check, ExpenseStats


# ---------------------------------------------------------------------------
# expense_should_count_check
# ---------------------------------------------------------------------------

class TestExpenseShouldCountCheck:
    def test_valid_expense(self):
        row = {'Category': 'Restaurants', 'Amount': '-45.00'}
        excluded = {'Credit Card Payments', 'Transfers'}
        assert expense_should_count_check(row, excluded) is True

    def test_excluded_category_skipped(self):
        row = {'Category': 'Credit Card Payments', 'Amount': '-200.00'}
        excluded = {'Credit Card Payments'}
        assert expense_should_count_check(row, excluded) is False

    def test_positive_amount_skipped(self):
        """Positive amounts are income/refunds — should not be processed."""
        row = {'Category': 'Restaurants', 'Amount': '10.00'}
        assert expense_should_count_check(row, set()) is False

    def test_zero_amount_skipped(self):
        row = {'Category': 'Restaurants', 'Amount': '0'}
        assert expense_should_count_check(row, set()) is False

    def test_invalid_amount_skipped(self):
        row = {'Category': 'Restaurants', 'Amount': 'not-a-number'}
        assert expense_should_count_check(row, set()) is False

    def test_missing_amount_skipped(self):
        row = {'Category': 'Restaurants'}
        assert expense_should_count_check(row, set()) is False


# ---------------------------------------------------------------------------
# ExpenseStats
# ---------------------------------------------------------------------------

class TestExpenseStats:
    def test_add_processed_accumulates(self):
        stats = ExpenseStats()
        stats.add_processed(50.0, 1.5, 'Restaurants')
        stats.add_processed(20.0, 0.4, 'Groceries')

        summary = stats.get_summary()
        assert summary['processed'] == 2
        assert summary['total_amount'] == pytest.approx(70.0)
        assert summary['total_cashback'] == pytest.approx(1.9)
        assert summary['net_amount'] == pytest.approx(68.1)

    def test_category_breakdown(self):
        stats = ExpenseStats()
        stats.add_processed(30.0, 0.9, 'Restaurants')
        stats.add_processed(10.0, 0.3, 'Restaurants')

        breakdown = stats.get_summary()['category_breakdown']
        assert breakdown['Restaurants'] == pytest.approx(40.0)

    def test_add_failed_records_error(self):
        stats = ExpenseStats()
        stats.add_failed("bad row")

        summary = stats.get_summary()
        assert summary['failed'] == 1
        assert "bad row" in summary['errors']

    def test_add_skipped(self):
        stats = ExpenseStats()
        stats.add_skipped("excluded category")

        assert stats.get_summary()['skipped'] == 1
