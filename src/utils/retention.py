import os
import glob
import time


RETENTION_DAYS = 365


def prune_old_files(directory: str, pattern: str, max_age_days: int = RETENTION_DAYS) -> int:
    """
    Delete files matching pattern in directory older than max_age_days.

    Args:
        directory: Directory to scan
        pattern: Glob pattern to match files against (e.g. '*.log')
        max_age_days: Maximum file age in days before deletion

    Returns:
        Number of files deleted
    """
    if not os.path.isdir(directory):
        return 0

    cutoff = time.time() - max_age_days * 86400
    deleted = 0

    for path in glob.glob(os.path.join(directory, pattern)):
        try:
            if os.path.getmtime(path) < cutoff:
                os.remove(path)
                deleted += 1
        except OSError:
            continue

    return deleted
