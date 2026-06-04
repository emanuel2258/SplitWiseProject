# Project Structure

## Overview
```
SplitWiseProject/
├── run.py                      # ⭐ MAIN ENTRY POINT - Start here!
├── process_monthly.py          # 🔄 Helper to auto-find latest transactions
├── add_transaction.py          # ➕ Add single transaction manually
├── config.json                 # ⚙️  Card cashback configuration
├── .env                        # 🔐 Environment variables (API keys, paths)
├── requirements.txt            # 📦 Python dependencies
├── README.md                   # 📖 Complete documentation
│
├── src/                        # Source code modules
│   ├── core/                   # Core business logic
│   │   ├── expense_tracker.py  # Expense processing & statistics
│   │   └── splitwise_client.py # Splitwise API integration
│   │
│   └── utils/                  # Utility modules
│       ├── logger.py           # Logging configuration
│       ├── config_loader.py    # Configuration management
│       └── cli.py              # Command-line interface
│
├── docs/                       # Documentation
│   ├── MIGRATION_GUIDE.md      # Upgrade from old version
│   └── QUICK_START_TRANSACTION.md  # Quick start for single transactions
│
├── legacy/                     # Deprecated files (kept for reference)
│   ├── main.py                 # Old entry point
│   ├── expenses.py             # Old expense module
│   └── splitwise.py            # Old Splitwise module
│
└── logs/                       # Log files (auto-generated)
    └── expense_tracker_*.log
```

## Quick Start Guide

### 1️⃣ First Time Setup
```bash
# Install dependencies
pip3 install -r requirements.txt

# Configure your cards in config.json
# Set up .env file with your API keys
```

### 2️⃣ Process Monthly Expenses

**Option A: Automatic (Recommended)**
```bash
python3 process_monthly.py
```
Automatically finds and processes the latest transaction file.

**Option B: Manual**
```bash
python3 run.py --input "path/to/transactions.csv" --dry-run
```
Specify exact file and preview before uploading.

**Option C: Interactive**
```bash
python3 run.py --interactive
```
Guided prompts for all options.

### 3️⃣ Add Single Transaction
```bash
python3 add_transaction.py
```
Or use the integrated command:
```bash
python3 run.py --add-transaction
```

## File Purposes

### Main Scripts (Root Directory)

| File | Purpose | When to Use |
|------|---------|-------------|
| **run.py** | Main application entry point | Process CSV files, upload to Splitwise |
| **process_monthly.py** | Auto-find latest transactions | Monthly expense processing |
| **add_transaction.py** | Add single transaction | Quick one-off expenses |

### Configuration Files

| File | Purpose | How to Edit |
|------|---------|-------------|
| **config.json** | Card cashback rates, excluded categories | Edit directly when rates change |
| **.env** | API keys, file paths | Edit for credentials/paths |
| **requirements.txt** | Python dependencies | Run `pip3 install -r requirements.txt` |

### Source Code (src/)

| Module | Purpose |
|--------|---------|
| **src/core/expense_tracker.py** | Process expenses, calculate cashback, generate reports |
| **src/core/splitwise_client.py** | Communicate with Splitwise API, handle uploads |
| **src/utils/logger.py** | Configure logging system |
| **src/utils/config_loader.py** | Load and validate configuration |
| **src/utils/cli.py** | Command-line interface and prompts |

### Documentation (docs/)

| File | Purpose |
|------|---------|
| **docs/MIGRATION_GUIDE.md** | How to upgrade from old version |
| **docs/QUICK_START_TRANSACTION.md** | Quick guide for single transactions |

### Legacy Files (legacy/)

⚠️ **Do not use these files** - kept only for reference
- `legacy/main.py` - Old entry point (use `run.py` instead)
- `legacy/expenses.py` - Old expense module
- `legacy/splitwise.py` - Old Splitwise module

## Execution Flow

### Processing CSV File
```
run.py
  ↓
Load .env variables
  ↓
Parse command-line arguments
  ↓
Load config.json (via config_loader.py)
  ↓
Process expenses (via expense_tracker.py)
  ↓
Calculate cashback
  ↓
Generate reports
  ↓
Upload to Splitwise (via splitwise_client.py)
  ↓
Save logs (via logger.py)
```

### Adding Single Transaction
```
add_transaction.py
  ↓
Prompt for transaction details
  ↓
Calculate cashback (via config_loader.py)
  ↓
Format for Splitwise
  ↓
Upload (via splitwise_client.py)
  ↓
Save logs (via logger.py)
```

## Common Tasks

### Update Cashback Rates
1. Open `config.json`
2. Find your card under `"cards"`
3. Update the cashback percentage (e.g., `0.03` = 3%)
4. Save file - changes take effect immediately

### Add New Credit Card
1. Open `config.json`
2. Add new entry under `"cards"`:
```json
"New Card - Ending in 1234": {
  "categories": {
    "Restaurants": 0.05,
    "Groceries": 0.03
  },
  "default_cashback": 0.01
}
```
3. Save file

### Change File Paths
1. Open `.env`
2. Update `CSV_READ_PATH` and `CSV_WRITE_PATH`
3. Save file

### View Logs
```bash
tail -f logs/expense_tracker_*.log
```

### Clean Up Old Logs
```bash
rm logs/expense_tracker_2024*.log
```

## Development Notes

### Adding New Features
- Core logic goes in `src/core/`
- Utilities go in `src/utils/`
- Update imports in `run.py` if needed
- Add tests for new functionality

### Module Dependencies
```
run.py
  ├── src.utils.logger
  ├── src.utils.config_loader
  ├── src.utils.cli
  ├── src.core.expense_tracker
  │   ├── src.utils.logger
  │   └── src.utils.config_loader
  └── src.core.splitwise_client
      ├── src.utils.logger
      └── src.utils.config_loader
```

### Import Pattern
All imports use absolute paths from project root:
```python
from src.utils.logger import get_logger
from src.core.expense_tracker import process_expenses
```

## Troubleshooting

### "ModuleNotFoundError"
- Ensure you're running from project root directory
- Check that `src/__init__.py` files exist
- Verify Python path includes project root

### "File not found"
- Check paths in `.env` file
- Use absolute paths if relative paths fail
- Verify file exists: `ls -la path/to/file`

### "Import errors after reorganization"
- All imports should use `src.` prefix
- Check `__init__.py` files exist in all directories
- Restart Python interpreter if needed

## Best Practices

1. **Always run dry-run first**: `--dry-run` flag
2. **Review logs after processing**: Check `logs/` directory
3. **Backup config.json**: Before making changes
4. **Test with old data**: When updating cashback rates
5. **Keep .env secure**: Never commit to git

## Migration from Old Structure

If you have old code referencing:
- `import expenses` → Use `from src.core import expense_tracker`
- `import splitwise` → Use `from src.core import splitwise_client`
- `import logger` → Use `from src.utils import logger`
- `import config_loader` → Use `from src.utils import config_loader`

See `docs/MIGRATION_GUIDE.md` for complete migration instructions.