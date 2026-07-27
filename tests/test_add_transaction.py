"""
Tests for add_transaction.py — quick-add transaction handling.
"""
import pytest
from add_transaction import (
    add_single_transaction,
    calculate_transaction_amount,
    format_transaction_for_expense,
)


@pytest.fixture
def config():
    return {
        "cards": {
            "savor": {
                "categories": {"Restaurants": 0.03},
                "default_cashback": 0.01
            }
        }
    }


class TestAddSingleTransaction:
    def test_requires_description_category_amount(self):
        with pytest.raises(ValueError):
            add_single_transaction(description=None, category="Restaurants", amount=10.0)

    def test_defaults_date_to_today_when_missing(self):
        transaction = add_single_transaction(
            description="Dinner", category="Restaurants", amount=10.0
        )
        assert 'date' in transaction

    def test_normalizes_slash_date_format(self):
        transaction = add_single_transaction(
            date="03/15/26", description="Dinner", category="Restaurants", amount=10.0
        )
        assert transaction['date'] == "2026-03-15"

    def test_normalizes_iso_date_format(self):
        transaction = add_single_transaction(
            date="2026-03-15", description="Dinner", category="Restaurants", amount=10.0
        )
        assert transaction['date'] == "2026-03-15"

    def test_invalid_date_raises_value_error(self):
        with pytest.raises(ValueError):
            add_single_transaction(
                date="not-a-date", description="Dinner", category="Restaurants", amount=10.0
            )

    def test_optional_account_is_preserved(self):
        transaction = add_single_transaction(
            description="Dinner", category="Restaurants", amount=10.0, account="Savor Card"
        )
        assert transaction['account'] == "Savor Card"

    def test_account_omitted_when_not_provided(self):
        transaction = add_single_transaction(
            description="Dinner", category="Restaurants", amount=10.0
        )
        assert 'account' not in transaction


class TestCalculateTransactionAmount:
    def test_no_account_returns_original_amount(self, config):
        transaction = {"amount": 100.0, "category": "Restaurants"}
        assert calculate_transaction_amount(transaction, config) == 100.0

    def test_applies_cashback_for_known_card(self, config):
        transaction = {"amount": 100.0, "category": "Restaurants", "account": "savor"}
        assert calculate_transaction_amount(transaction, config) == 97.0


class TestFormatTransactionForExpense:
    def test_formats_expected_fields(self, config):
        transaction = {
            "date": "2026-03-15",
            "description": "Dinner",
            "category": "Restaurants",
            "amount": 100.0,
        }
        expense = format_transaction_for_expense(transaction, config)
        assert expense == {
            "date": "2026-03-15",
            "description": "Dinner",
            "category": "Restaurants",
            "amount": "100.0",
        }
