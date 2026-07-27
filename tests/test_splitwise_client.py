"""
Tests for src/core/splitwise_client.py — duplicate detection and upload log.
"""
import json
import os
from datetime import datetime, timedelta
import pytest
from src.core.splitwise_client import SplitwiseClient
from src.utils.retention import RETENTION_DAYS


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


class TestUploadLogRetention:
    def test_entries_older_than_retention_are_dropped(self, tmp_path, config):
        log_file = tmp_path / "uploaded_log.json"
        old_date = (datetime.now() - timedelta(days=RETENTION_DAYS + 10)).strftime('%Y-%m-%d')
        recent_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        log_file.write_text(json.dumps({
            'uploaded': [
                f"{old_date}|Old Dinner|25.00",
                f"{recent_date}|Recent Dinner|25.00",
            ]
        }))

        client = SplitwiseClient("key", config, dry_run=True, log_path=str(log_file))

        assert dict(client.uploaded_expenses) == {f"{recent_date}|Recent Dinner|25.00": 1}

    def test_pruning_is_persisted_to_disk(self, tmp_path, config):
        log_file = tmp_path / "uploaded_log.json"
        old_date = (datetime.now() - timedelta(days=RETENTION_DAYS + 10)).strftime('%Y-%m-%d')
        log_file.write_text(json.dumps({'uploaded': [f"{old_date}|Old Dinner|25.00"]}))

        SplitwiseClient("key", config, dry_run=True, log_path=str(log_file))

        with open(log_file) as f:
            data = json.load(f)
        assert data['uploaded'] == []

    def test_unparseable_key_date_is_kept(self, tmp_path, config):
        log_file = tmp_path / "uploaded_log.json"
        log_file.write_text(json.dumps({'uploaded': ["not-a-date|Dinner|25.00"]}))

        client = SplitwiseClient("key", config, dry_run=True, log_path=str(log_file))

        assert "not-a-date|Dinner|25.00" in client.uploaded_expenses


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

    def test_dry_run_does_not_persist_to_upload_log(self, client, expense):
        """A dry-run upload must not mark the expense as uploaded in the persistent log,
        since nothing was actually sent to Splitwise."""
        stats = client.upload_expenses([expense], group_id="12345")
        assert stats['uploaded'] == 1
        assert client.is_duplicate(expense) is False
        assert not os.path.exists(client.log_path)


class TestBatchDuplicateDetection:
    """Occurrence-aware duplicate detection: legitimate same-day repeats within a
    single batch should upload, while true re-uploads of already-uploaded expenses
    should still be skipped."""

    def test_two_identical_new_expenses_in_one_batch_both_upload(self, client, expense):
        stats = client.upload_expenses([expense, expense], group_id="12345")
        assert stats['uploaded'] == 2
        assert stats['skipped'] == 0

    def test_one_prior_upload_skips_only_one_occurrence_in_batch(self, client, expense):
        client.mark_as_uploaded(expense)  # simulates one real prior upload
        stats = client.upload_expenses([expense, expense], group_id="12345")
        assert stats['skipped'] == 1
        assert stats['uploaded'] == 1

    def test_rerunning_a_fully_uploaded_batch_skips_all(self, client, expense):
        client.mark_as_uploaded(expense)
        client.mark_as_uploaded(expense)  # two prior uploads of the same key
        stats = client.upload_expenses([expense, expense], group_id="12345")
        assert stats['skipped'] == 2
        assert stats['uploaded'] == 0
