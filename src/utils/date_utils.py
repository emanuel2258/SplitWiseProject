from datetime import datetime
from src.utils.logger import get_logger


"""
Shared date parsing utilities for the expense tracker application.
"""


logger = get_logger()


def parse_expense_date(date_str: str) -> str:
    """
    Parse a date string into YYYY-MM-DD format.

    Supports: MM/DD/YY, MM/DD/YYYY, YYYY-MM-DD, YYYY/MM/DD.

    Args:
        date_str: Date string in any of the supported formats.

    Returns:
        Date string in YYYY-MM-DD format.

    Raises:
        ValueError: If the date string cannot be parsed.
    """
    date_formats = [
        '%Y-%m-%d',   # 2026-03-15
        '%m/%d/%y',   # 03/15/26
        '%m/%d/%Y',   # 03/15/2026
        '%Y/%m/%d',   # 2026/03/15
    ]

    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
        except ValueError:
            continue

    # Manual fallback for non-standard separators
    try:
        parts = date_str.replace('/', '-').split('-')
        if len(parts) == 3:
            if len(parts[0]) == 4:
                year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
            else:
                month, day, year = int(parts[0]), int(parts[1]), int(parts[2])
                if year < 100:
                    year = 2000 + year if year < 50 else 1900 + year
            return f"{year:04d}-{month:02d}-{day:02d}"
    except (ValueError, IndexError):
        pass

    raise ValueError(f"Could not parse date '{date_str}'")
