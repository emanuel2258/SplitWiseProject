"""
Tests for src/core/expense_tracker.py
"""
import pytest
from src.core.expense_tracker import (
    expense_should_count_check,
    ExpenseStats,
    filter_and_calculate_expenses_from_csv,
)


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


class TestSummaryArithmetic:
    """Regression: total_amount used to accumulate the POST-cashback amount while
    get_summary() subtracted cashback again, so net_amount double-counted it and
    'Total amount' silently reported the net. Uploads were always correct - only
    the report lied - but it meant a month never reconciled against a statement."""

    def test_total_amount_is_gross_and_net_subtracts_cashback_once(self):
        stats = ExpenseStats()
        # $100.00 charged, 3% back -> $97.00 actually owed
        stats.add_processed(100.00, 3.00, 'Groceries')
        # $50.00 charged, 1% back -> $49.50 actually owed
        stats.add_processed(50.00, 0.50, 'Restaurants')

        summary = stats.get_summary()
        assert summary['total_amount'] == 150.00      # as charged
        assert summary['total_cashback'] == 3.50
        assert summary['net_amount'] == 146.50        # gross - cashback, once

    def test_net_amount_matches_what_gets_uploaded(self, tmp_path):
        """The net total must equal the sum of the per-expense amounts the
        uploader actually sends."""
        csv_file = tmp_path / "expenses.csv"
        csv_file.write_text(
            "Date,Description,Category,Amount,Account\n"
            "08/01/26,Store A,Groceries,-100.00,Test Card\n"
            "08/02/26,Store B,Groceries,-50.00,Test Card\n"
        )
        config = {
            "cards": {"Test Card": {"categories": {"Groceries": 0.10},
                                    "default_cashback": 0.10}},
            "excluded_categories": [],
        }
        expenses, stats = filter_and_calculate_expenses_from_csv(str(csv_file), config)

        uploaded_total = round(sum(float(e['amount']) for e in expenses), 2)
        summary = stats.get_summary()

        assert summary['total_amount'] == 150.00       # what the cards were charged
        assert summary['net_amount'] == uploaded_total  # what actually gets sent
        assert uploaded_total == 135.00                 # 150 less 10%

    def test_category_breakdown_is_gross(self):
        stats = ExpenseStats()
        stats.add_processed(100.00, 3.00, 'Groceries')
        assert stats.get_summary()['category_breakdown']['Groceries'] == 100.00
