"""
Tests for src/utils/config_loader.py
"""
import pytest
from src.utils.config_loader import get_card_cashback, get_excluded_categories


# ---------------------------------------------------------------------------
# Shared fixture config
# ---------------------------------------------------------------------------

@pytest.fixture
def config():
    return {
        "card_aliases": {
            "Citi Custom Cash Card - Ending in 9673": "citi_custom_cash",
            "Amazon Credit Card - Ending in 7980": "amazon_card",
            "Discover It Card - Ending in 7693": "discover_it",
        },
        "cards": {
            "citi_custom_cash": {
                "categories": {
                    "Restaurants": [
                        {"rate": 0.05, "valid_from": "2026-01-01", "valid_until": "2026-12-31"}
                    ]
                },
                "default_cashback": 0.01
            },
            "amazon_card": {
                "categories": {"*": 0.05},
                "default_cashback": 0.05
            },
            "discover_it": {
                "categories": {
                    "Restaurants": [
                        {"rate": 0.05, "valid_from": "2026-07-01", "valid_until": "2026-09-30"}
                    ]
                },
                "default_cashback": 0.01
            },
            "savor": {
                "categories": {
                    "Restaurants": 0.03,
                    "Groceries": 0.03,
                },
                "default_cashback": 0.01
            }
        },
        "excluded_categories": ["Credit Card Payments", "Transfers"]
    }


# ---------------------------------------------------------------------------
# Alias resolution
# ---------------------------------------------------------------------------

class TestAliasResolution:
    def test_full_name_resolves_to_alias(self, config):
        rate = get_card_cashback(
            config,
            "Citi Custom Cash Card - Ending in 9673",
            "Restaurants",
            "2026-05-15"
        )
        assert rate == 0.05

    def test_alias_used_directly(self, config):
        rate = get_card_cashback(config, "savor", "Restaurants")
        assert rate == 0.03

    def test_unknown_card_returns_default(self, config):
        rate = get_card_cashback(config, "Unknown Card", "Restaurants")
        assert rate == 0.01


# ---------------------------------------------------------------------------
# Plain float rates (always valid)
# ---------------------------------------------------------------------------

class TestPlainFloatRates:
    def test_plain_float_category_rate(self, config):
        assert get_card_cashback(config, "savor", "Restaurants") == 0.03

    def test_plain_float_default_cashback(self, config):
        assert get_card_cashback(config, "savor", "Travel") == 0.01

    def test_wildcard_rate(self, config):
        assert get_card_cashback(config, "amazon_card", "Anything") == 0.05


# ---------------------------------------------------------------------------
# Date-bounded rates
# ---------------------------------------------------------------------------

class TestDateBoundedRates:
    def test_rate_valid_within_window(self, config):
        rate = get_card_cashback(
            config, "citi_custom_cash", "Restaurants", "2026-06-15"
        )
        assert rate == 0.05

    def test_rate_falls_back_outside_window(self, config):
        """discover_it Restaurants is only valid July–Sep 2026."""
        rate = get_card_cashback(
            config, "discover_it", "Restaurants", "2026-05-01"
        )
        assert rate == 0.01  # falls back to default_cashback

    def test_rate_valid_on_boundary_start(self, config):
        rate = get_card_cashback(
            config, "discover_it", "Restaurants", "2026-07-01"
        )
        assert rate == 0.05

    def test_rate_valid_on_boundary_end(self, config):
        rate = get_card_cashback(
            config, "discover_it", "Restaurants", "2026-09-30"
        )
        assert rate == 0.05

    def test_rate_expired_after_window(self, config):
        rate = get_card_cashback(
            config, "discover_it", "Restaurants", "2026-10-01"
        )
        assert rate == 0.01

    def test_no_expense_date_uses_today(self, config):
        """Should not raise — uses today's date as fallback."""
        rate = get_card_cashback(config, "savor", "Groceries")
        assert rate == 0.03


# ---------------------------------------------------------------------------
# Excluded categories
# ---------------------------------------------------------------------------

class TestExcludedCategories:
    def test_returns_excluded_list(self, config):
        excluded = get_excluded_categories(config)
        assert "Credit Card Payments" in excluded
        assert "Transfers" in excluded

    def test_empty_config_returns_empty_list(self):
        assert get_excluded_categories({}) == []
