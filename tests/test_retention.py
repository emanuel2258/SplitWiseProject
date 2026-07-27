"""
Tests for src/utils/retention.py — file retention/pruning helper.
"""
import os
import time
import pytest
from src.utils.retention import prune_old_files, RETENTION_DAYS


def _touch_with_age(path, age_days):
    with open(path, 'w') as f:
        f.write('data')
    old_time = time.time() - age_days * 86400
    os.utime(path, (old_time, old_time))


class TestPruneOldFiles:
    def test_deletes_files_older_than_max_age(self, tmp_path):
        old_file = tmp_path / "old.log"
        _touch_with_age(old_file, RETENTION_DAYS + 10)

        deleted = prune_old_files(str(tmp_path), '*.log')

        assert deleted == 1
        assert not old_file.exists()

    def test_keeps_recent_files(self, tmp_path):
        recent_file = tmp_path / "recent.log"
        _touch_with_age(recent_file, 5)

        deleted = prune_old_files(str(tmp_path), '*.log')

        assert deleted == 0
        assert recent_file.exists()

    def test_only_matches_given_pattern(self, tmp_path):
        old_txt = tmp_path / "old.txt"
        _touch_with_age(old_txt, RETENTION_DAYS + 10)

        deleted = prune_old_files(str(tmp_path), '*.log')

        assert deleted == 0
        assert old_txt.exists()

    def test_nonexistent_directory_is_a_no_op(self, tmp_path):
        missing_dir = str(tmp_path / "does_not_exist")
        assert prune_old_files(missing_dir, '*.log') == 0
