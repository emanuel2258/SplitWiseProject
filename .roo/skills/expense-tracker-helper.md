# Expense Tracker Helper Skill

## Overview
This skill helps manage and operate the SplitWise expense tracking application. It provides context about the project structure, common operations, and troubleshooting guidance.

## Project Context

### Purpose
Automated expense tracking system that:
- Processes CSV expense files from Empower
- Calculates net expenses after cashback
- Uploads expenses to Splitwise for group expense sharing
- Generates detailed reports and summaries

### Key Directories
- **Project Root:** `/Users/emanuelmartinez/Documents/GitHub/SplitWiseProject`
- **Transaction Files:** `../../empower_data/Transactions/`
- **Generated Files:** `../../empower_data/Generated/`
- **Logs:** `logs/`

### Configuration Files
- **`.env`** - Environment variables (API keys, paths)
- **`config.json`** - Card cashback rates and excluded categories
- **`requirements.txt`** - Python dependencies

## Common Operations

### 1. Process Monthly Expenses (Dry Run)
```bash
python3 run.py --input "../../empower_data/Transactions/YYYY-MM-DD thru YYYY-MM-DD transactions.csv" --dry-run
```

**When to use:** Preview expenses before uploading to Splitwise

### 2. Upload Expenses to Splitwise
```bash
python3 run.py --input "../../empower_data/Transactions/YYYY-MM-DD thru YYYY-MM-DD transactions.csv"
```

**When to use:** After reviewing dry run results and ready to upload

### 3. Process Latest Transaction File
```bash
python3 process_monthly.py
```

**When to use:** Automatically find and process the most recent transaction file

### 4. Interactive Mode
```bash
python3 run.py --interactive
```

**When to use:** Guided prompts for all options

### 5. Add Single Transaction
```bash
python3 add_transaction.py
```

**When to use:** Manually add a single expense without CSV file

## Configuration Management

### Update Cashback Rates
Edit `config.json`:
```json
{
  "cards": {
    "Card Name - Ending in XXXX": {
      "categories": {
        "Category Name": 0.05
      },
      "default_cashback": 0.01
    }
  }
}
```

### Add New Card
1. Open `config.json`
2. Add new card entry under `"cards"`
3. Specify category cashback rates
4. Set default cashback rate
5. Save file - changes take effect immediately

### Update Excluded Categories
Edit `config.json` → `"excluded_categories"` array:
```json
{
  "excluded_categories": [
    "Credit Card Payments",
    "Transfers",
    "Refunds & Reimbursements"
  ]
}
```

### Update Environment Variables
Edit `.env` file:
```bash
CSV_READ_PATH=../../empower_data/Transactions/
CSV_WRITE_PATH=../../empower_data/Generated/
SPLITWISE_API_KEY=your_key_here
SPLITWISE_GROUP_ID=your_group_id
```

## File Structure

### Core Application Files
- **`run.py`** - Main entry point with CLI
- **`expense_tracker.py`** - Expense processing logic
- **`splitwise_client.py`** - Splitwise API client
- **`config_loader.py`** - Configuration management
- **`logger.py`** - Logging system
- **`cli.py`** - Command-line interface

### Helper Scripts
- **`process_monthly.py`** - Auto-find latest transaction file
- **`add_transaction.py`** - Add single transaction manually

### Documentation
- **`README.md`** - Complete usage guide
- **`MIGRATION_GUIDE.md`** - Migration from old version
- **`QUICK_START_TRANSACTION.md`** - Quick start for single transactions

### Legacy Files (Deprecated)
- **`main.py`** - Old entry point (use `run.py` instead)
- **`expenses.py`** - Old expense module (use `expense_tracker.py`)
- **`splitwise.py`** - Old Splitwise module (use `splitwise_client.py`)

## Output Files

### Generated During Processing
- **Modified CSV:** `Modified_YYYY-MM-DD thru YYYY-MM-DD transactions.csv`
  - Location: Same as input or `CSV_WRITE_PATH`
  - Contains: Processed expenses with cashback applied

- **Summary JSON:** `summary_YYYYMMDD_HHMMSS.json`
  - Location: Project root
  - Contains: Statistics, category breakdown, errors

- **Log Files:** `logs/expense_tracker_YYYYMMDD_HHMMSS.log`
  - Location: `logs/` directory
  - Contains: Detailed operation logs

## Troubleshooting

### Issue: "Card not found in configuration"
**Solution:** Add card to `config.json` with exact name from CSV

### Issue: "Missing environment variables"
**Solution:** Check `.env` file exists and contains all required variables

### Issue: "File not found"
**Solution:** Verify file path is correct, use absolute path if needed

### Issue: Incorrect cashback amounts
**Solution:** 
1. Run with `--dry-run` to see calculations
2. Verify card name matches exactly in `config.json`
3. Check category name matches

### Issue: Expenses not uploading
**Solution:**
1. Verify API key is valid at https://secure.splitwise.com/apps
2. Check group ID is correct
3. Review log file for detailed errors

### Issue: Duplicate expenses
**Solution:** Built-in duplicate detection prevents this automatically

## Best Practices

### Monthly Workflow
1. Export transactions from Empower as CSV
2. Save to `../../empower_data/Transactions/`
3. Run dry run: `python3 run.py --input "FILE.csv" --dry-run`
4. Review summary and verify amounts
5. Check log file if any issues
6. Upload: `python3 run.py --input "FILE.csv"`
7. Verify in Splitwise web interface

### Updating Cashback Rates
1. When card rates change, update `config.json` immediately
2. Test with dry run on old transaction file
3. Compare results to ensure accuracy

### Log Management
- Logs automatically saved to `logs/` directory
- Review logs when troubleshooting
- Old logs can be deleted periodically
- Logs are excluded from git via `.gitignore`

## Command Reference

### All Available Options
```bash
python3 run.py [OPTIONS]

Options:
  --input, -i          Path to input CSV file
  --output, -o         Path for output CSV file
  --config, -c         Path to config file (default: config.json)
  --group-id, -g       Splitwise group ID
  --api-key, -k        Splitwise API key
  --dry-run, -d        Preview without uploading
  --summary-only, -s   Generate report only
  --interactive, -I    Interactive mode
  --skip-duplicates    Skip duplicate expenses (default: true)
  --verbose, -v        Enable verbose logging
```

## Environment Variables

### Required
- `SPLITWISE_API_KEY` - Your Splitwise API key
- `SPLITWISE_GROUP_ID` - Your Splitwise group ID

### Optional
- `CSV_READ_PATH` - Default input directory
- `CSV_WRITE_PATH` - Default output directory
- `PYTHONUNBUFFERED` - Python output buffering (set to 1)

## Quick Reference

### Find Latest Transaction File
```bash
ls -lt ../../empower_data/Transactions/*.csv | head -1
```

### View Recent Logs
```bash
tail -f logs/expense_tracker_*.log
```

### Check Summary
```bash
cat summary_*.json | python3 -m json.tool
```

### Clean Test Data
```bash
rm -f sample_expenses.csv Modified_*.csv summary_*.json
```

## Integration Points

### With Empower
- Export transactions as CSV
- Save to configured `CSV_READ_PATH`
- File format: Date, Account, Description, Category, Tags, Amount

### With Splitwise
- Uses Splitwise API v3.0
- Requires API key from https://secure.splitwise.com/apps
- Uploads to specified group ID
- Splits expenses equally by default

## Version Information

### Current Version
- Python 3.11+
- Dependencies: requests>=2.31.0, python-dotenv>=1.0.0

### Recent Updates
- Added dry run mode
- Implemented duplicate detection
- Added comprehensive logging
- Created interactive CLI
- Moved logs to dedicated directory
- Added .env file support

## Support Resources

- **README.md** - Full documentation
- **MIGRATION_GUIDE.md** - Upgrade from old version
- **Log files** - Detailed operation logs
- **Summary JSON** - Processing statistics

## Notes for AI Assistant

When helping with this project:
1. Always suggest dry run first before actual upload
2. Check `.env` and `config.json` for current configuration
3. Review recent log files for context on issues
4. Verify file paths are correct (relative to project root)
5. Remind user to backup data before major changes
6. Suggest testing with old transaction files when making config changes
7. Check that card names in CSV exactly match config.json
8. Verify Splitwise credentials are valid if upload fails