"""
Tests for src/utils/cli.py — argument parsing and input validation.
"""
import argparse
import pytest
from src.utils.cli import (
    create_argument_parser,
    validate_inputs,
    prompt_for_input,
    prompt_yes_no,
)


@pytest.fixture
def parser():
    return create_argument_parser()


class TestArgumentDefaults:
    def test_skip_duplicates_defaults_to_true(self, parser):
        args = parser.parse_args(['--input', 'expenses.csv'])
        assert args.skip_duplicates is True

    def test_no_skip_duplicates_flag_disables_it(self, parser):
        args = parser.parse_args(['--input', 'expenses.csv', '--no-skip-duplicates'])
        assert args.skip_duplicates is False

    def test_group_id_has_default(self, parser):
        args = parser.parse_args(['--input', 'expenses.csv'])
        assert args.group_id == '9168077'

    def test_config_has_default(self, parser):
        args = parser.parse_args(['--input', 'expenses.csv'])
        assert args.config == 'config.json'

    def test_dry_run_and_summary_only_default_false(self, parser):
        args = parser.parse_args(['--input', 'expenses.csv'])
        assert args.dry_run is False
        assert args.summary_only is False


class TestValidateInputs:
    def _namespace(self, **overrides):
        base = dict(
            add_transaction=False,
            transaction_description=None,
            transaction_category=None,
            transaction_amount=None,
            interactive=False,
            input=None,
        )
        base.update(overrides)
        return argparse.Namespace(**base)

    def test_add_transaction_mode_always_valid(self):
        args = self._namespace(add_transaction=True)
        assert validate_inputs(args) is True

    def test_complete_quick_transaction_is_valid(self):
        args = self._namespace(
            transaction_description="Dinner",
            transaction_category="Restaurants",
            transaction_amount=45.50,
        )
        assert validate_inputs(args) is True

    def test_partial_quick_transaction_is_invalid(self):
        args = self._namespace(
            transaction_description="Dinner",
            transaction_category=None,
            transaction_amount=45.50,
        )
        assert validate_inputs(args) is False

    def test_csv_mode_without_input_is_invalid(self):
        args = self._namespace(input=None, interactive=False)
        assert validate_inputs(args) is False

    def test_csv_mode_with_input_is_valid(self):
        args = self._namespace(input='expenses.csv')
        assert validate_inputs(args) is True

    def test_interactive_mode_without_input_is_valid(self):
        args = self._namespace(input=None, interactive=True)
        assert validate_inputs(args) is True


class TestPrompts:
    def test_prompt_for_input_returns_default_on_empty(self, monkeypatch):
        monkeypatch.setattr('builtins.input', lambda _: '')
        assert prompt_for_input("Enter path", default="expenses.csv") == "expenses.csv"

    def test_prompt_for_input_returns_typed_value(self, monkeypatch):
        monkeypatch.setattr('builtins.input', lambda _: 'my_file.csv')
        assert prompt_for_input("Enter path", default="expenses.csv") == "my_file.csv"

    def test_prompt_yes_no_default_on_empty(self, monkeypatch):
        monkeypatch.setattr('builtins.input', lambda _: '')
        assert prompt_yes_no("Proceed?", default=True) is True
        assert prompt_yes_no("Proceed?", default=False) is False

    def test_prompt_yes_no_accepts_yes_no(self, monkeypatch):
        monkeypatch.setattr('builtins.input', lambda _: 'y')
        assert prompt_yes_no("Proceed?") is True

        monkeypatch.setattr('builtins.input', lambda _: 'n')
        assert prompt_yes_no("Proceed?") is False

    def test_prompt_yes_no_reprompts_on_invalid_input(self, monkeypatch, capsys):
        responses = iter(['maybe', 'y'])
        monkeypatch.setattr('builtins.input', lambda _: next(responses))
        assert prompt_yes_no("Proceed?") is True
        assert "Please enter 'y' or 'n'" in capsys.readouterr().out
