# Migration Guide: Old Version → New Version

This guide helps you migrate from the old `main.py` script to the new improved `run.py` version.

## Quick Migration

### Old Way (main.py)
```bash
export CSV_READ_PATH=/path/to/expenses/
export CSV_READ_FILE_NAME=march_expenses.csv
export CSV_WRITE_PATH=/path/to/output/
export SPLITWISE_API_KEY=your_api_key
export SPLITWISE_GROUP_ID=12345
python main.py
```

### New Way (run.py)
```bash
# Option 1: Command line arguments
python run.py --input /path/to/expenses/march_expenses.csv --group-id 12345

# Option 2: Interactive mode (recommended for first time)
python run.py --interactive

# Option 3: Dry run to preview first
python run.py --input /path/to/expenses/march_expenses.csv --dry-run
```

## What's Changed?

### 1. Configuration Management

**Old:** Hardcoded cashback rates in `expenses.py`
```python
cards_category_cashback = {
    "Savor - Ending in 9209": {
        "Restaurants": .03,
        ...
    }
}
```

**New:** External configuration file `config.json`
```json
{
  "cards": {
    "Savor - Ending in 9209": {
      "categories": {
        "Restaurants": 0.03
      }
    }
  }
}
```

**Benefits:**
- Update cashback rates without touching code
- Easy to add new cards
- Share configuration across team

### 2. Environment Variables

**Old:** Required all variables
```bash
CSV_READ_PATH=/path/to/
CSV_READ_FILE_NAME=file.csv
CSV_WRITE_PATH=/path/to/output/
SPLITWISE_API_KEY=key
SPLITWISE_GROUP_ID=123
```

**New:** Optional, can use command-line arguments
```bash
# Only need these if not using command-line args
SPLITWISE_API_KEY=key
SPLITWISE_GROUP_ID=123
```

### 3. Error Handling

**Old:** Silent failures or crashes
```python
if csv_reader.line_num == 1:
    print("File is empty")
    return None  # Could cause crashes later
```

**New:** Proper error handling with logging
```python
try:
    # Process expenses
except FileNotFoundError:
    logger.error(f"File not found: {file_path}")
    return expenses, stats  # Always returns valid data
```

### 4. New Features

#### Dry Run Mode
Preview expenses before uploading:
```bash
python run.py --input expenses.csv --dry-run
```

#### Summary Reports
Automatic generation of:
- Console summary with statistics
- JSON summary file
- Category breakdowns
- Cashback calculations

#### Duplicate Detection
Prevents uploading the same expense twice:
```python
# Automatically tracks and skips duplicates
if skip_duplicates and self.is_duplicate(expense):
    stats['skipped'] += 1
    continue
```

#### Interactive Mode
Guided prompts for all inputs:
```bash
python run.py --interactive
```

## Step-by-Step Migration

### Step 1: Create Configuration File

1. Copy your card information from `expenses.py` (lines 35-69)
2. Create `config.json` with this structure:

```json
{
  "cards": {
    "Your Card Name": {
      "categories": {
        "Category Name": 0.03
      },
      "default_cashback": 0.01
    }
  },
  "excluded_categories": [
    "Credit Card Payments",
    "Transfers"
  ]
}
```

### Step 2: Set Up Environment (Optional)

If you want to use environment variables:

```bash
cp .env.example .env
# Edit .env with your values
```

Or use command-line arguments (recommended).

### Step 3: Test with Dry Run

```bash
python run.py --input your_expenses.csv --dry-run
```

Review the output to ensure:
- All expenses are processed correctly
- Cashback calculations are accurate
- Categories are properly excluded

### Step 4: Upload to Splitwise

```bash
python run.py --input your_expenses.csv --group-id YOUR_GROUP_ID
```

## Troubleshooting Migration Issues

### Issue: "Card not found in configuration"

**Cause:** Card name in CSV doesn't match `config.json`

**Solution:** 
1. Check exact card name in your CSV
2. Add it to `config.json` with exact spelling
3. Include spaces and special characters

### Issue: "Missing environment variables"

**Cause:** Using old environment variable names

**Solution:** Use command-line arguments instead:
```bash
python run.py --input FILE --group-id ID --api-key KEY
```

### Issue: Different cashback amounts

**Cause:** Rounding differences or configuration mismatch

**Solution:**
1. Run with `--dry-run` to see calculations
2. Compare with old version
3. Adjust `config.json` if needed

### Issue: Expenses not uploading

**Cause:** API key or group ID incorrect

**Solution:**
1. Verify API key at https://secure.splitwise.com/apps
2. Check group ID in Splitwise URL
3. Use `--dry-run` to test without uploading

## Feature Comparison

| Feature | Old (main.py) | New (run.py) |
|---------|---------------|--------------|
| Configuration | Hardcoded | JSON file |
| Error Handling | Basic | Comprehensive |
| Logging | Print statements | Proper logging |
| Dry Run | No | Yes |
| Summary Reports | No | Yes |
| Duplicate Detection | No | Yes |
| Interactive Mode | No | Yes |
| Command-line Args | No | Yes |
| Progress Tracking | No | Yes |
| Validation | Minimal | Extensive |

## Backward Compatibility

The old files are still present for backward compatibility:
- `main.py` - Shows deprecation warning
- `expenses.py` - Shows deprecation warning
- `splitwise.py` - Shows deprecation warning

These will be removed in a future version. Please migrate to the new version.

## Getting Help

If you encounter issues during migration:

1. Check the [README.md](README.md) for detailed documentation
2. Review log files for error details
3. Use `--verbose` flag for more information
4. Try `--interactive` mode for guided setup

## Benefits of Migrating

✅ **Easier monthly updates** - Just edit `config.json`  
✅ **Safer operations** - Dry run mode prevents mistakes  
✅ **Better visibility** - Detailed logs and reports  
✅ **Time savings** - Interactive mode and better error messages  
✅ **Reliability** - Duplicate detection and proper error handling  
✅ **Flexibility** - Multiple ways to run (CLI, interactive, env vars)  

## Next Steps

After successful migration:

1. Delete or archive old CSV files
2. Set up monthly workflow using new version
3. Customize `config.json` for your needs
4. Consider automating with cron/scheduled tasks

---

**Questions?** Check the [README.md](README.md) or review the log files for detailed information.