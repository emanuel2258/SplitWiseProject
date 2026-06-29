"""
Tests for src/core/splitwise_client.py — duplicate detection and upload log.
"""
import json
import os
import pytest
from src.core.splitwise_client import SplitwiseClient


@pytest.fixture
def config():
    return {
        "splitwise": {
            "default_category_id": 18,
            "currency_code": "USD",
            "split_equally": True,
            "details_suffix": "Test"
        }
    }


@pytest.fixture
def expense():
    return {
        "date": "2026-05-15",
        "description": "Dinner at Cava",
        "category": "Restaurants",
        "amount": "25.00"
    }


@pytest.fixture
def client(tmp_path, config):
    log_file = str(tmp_path / "uploaded_log.json")
    return SplitwiseClient(
        api_key="test_key",
        config=config,
        dry_run=True,
        log_path=log_file
    )


class TestDuplicateDetection:
    def test_new_expense_is_not_duplicate(self, client, expense):
        assert client.is_duplicate(expense) is False

    def test_marked_expense_is_duplicate(self, client, expense):
        client.mark_as_uploaded(expense)
        assert client.is_duplicate(expense) is True

    def test_different_expense_is_not_duplicate(self, client, expense):
        client.mark_as_uploaded(expense)
        other = {**expense, "description": "Lunch at Cava"}
        assert client.is_duplicate(other) is False


class TestPersistentLog:
    def test_log_persists_across_instances(self, tmp_path, config, expense):
        log_file = str(tmp_path / "uploaded_log.json")

        client1 = SplitwiseClient("key", config, dry_run=True, log_path=log_file)
        client1.mark_as_uploaded(expense)

        client2 = SplitwiseClient("key", config, dry_run=True, log_path=log_file)
        assert client2.is_duplicate(expense) is True

    def test_log_file_written_on_mark(self, tmp_path, config, expense):
        log_file = str(tmp_path / "uploaded_log.json")
        client = SplitwiseClient("key", config, dry_run=True, log_path=log_file)
        client.mark_as_uploaded(expense)

        assert os.path.exists(log_file)
        with open(log_file) as f:
            data = json.load(f)
        assert len(data['uploaded']) == 1

    def test_missing_log_starts_fresh(self, tmp_path, config):
        log_file = str(tmp_path / "nonexistent_log.json")
        client = SplitwiseClient("key", config, dry_run=True, log_path=log_file)
        assert len(client.uploaded_expenses) == 0

    def test_corrupted_log_starts_fresh(self, tmp_path, config):
        log_file = tmp_path / "bad_log.json"
        log_file.write_text("not valid json")
        client = SplitwiseClient("key", config, dry_run=True, log_path=str(log_file))
        assert len(client.uploaded_expenses) == 0


class TestDryRunUpload:
    def test_dry_run_does_not_call_api(self, client, expense):
        """upload_expenses in dry-run mode should succeed without hitting the network."""
        stats = client.upload_expenses([expense], group_id="12345")
        assert stats['uploaded'] == 1
        assert stats['failed'] == 0

    def test_skip_duplicates_in_dry_run(self, client, expense):
        client.mark_as_uploaded(expense)
        stats = client.upload_expenses([expense], group_id="12345", skip_duplicates=True)
        assert stats['skipped'] == 1
        assert stats['uploaded'] == 0
