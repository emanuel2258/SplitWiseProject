# Expense Tracker & Splitwise Uploader

A Python application that processes expense CSV files, calculates cashback adjustments, and automatically uploads expenses to Splitwise.

## Features

- 📊 **CSV Processing**: Import expenses from CSV files with automatic date parsing
- ➕ **Single Transaction Entry**: Add individual transactions quickly without CSV files
- 💳 **Cashback Calculation**: Automatically calculates net expenses after cashback based on card and category
- 🔄 **Splitwise Integration**: Uploads expenses directly to your Splitwise group
- 🎯 **Duplicate Detection**: Prevents uploading the same expense multiple times
- 🔍 **Dry Run Mode**: Preview expenses before uploading
- 📈 **Summary Reports**: Detailed statistics and category breakdowns
- ⚙️ **Easy Configuration**: JSON-based configuration for cards and settings
- 🖥️ **Interactive CLI**: User-friendly command-line interface with prompts
- 📝 **Comprehensive Logging**: Track all operations with detailed logs

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd SplitWiseProject
```

2. Install required dependencies:
```bash
pip install requests
```

3. Set up your environment variables:
```bash
cp .env.example .env
# Edit .env with your actual values
```

4. Configure your cards and cashback rates in `config.json`

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
CSV_READ_PATH=/path/to/your/expenses/
CSV_READ_FILE_NAME=expenses.csv
CSV_WRITE_PATH=/path/to/output/
SPLITWISE_API_KEY=your_api_key_here
SPLITWISE_GROUP_ID=your_group_id_here
```

**Getting Your Splitwise API Key:**
1. Go to https://secure.splitwise.com/apps
2. Register a new application
3. Copy your API key

**Finding Your Group ID:**
1. Open your Splitwise group in a browser
2. The URL will look like: `https://secure.splitwise.com/#/groups/12345`
3. The number at the end (12345) is your group ID

### Card Configuration

Edit `config.json` to add or modify your credit cards and cashback rates:

```json
{
  "cards": {
    "Your Card Name - Ending in 1234": {
      "categories": {
        "Restaurants": 0.03,
        "Groceries": 0.02
      },
      "default_cashback": 0.01
    }
  }
}
```

**Cashback rates are in decimal format:**
- 0.01 = 1%
- 0.02 = 2%
- 0.03 = 3%
- 0.05 = 5%

**Special wildcard category:**
- Use `"*": 0.02` to apply cashback to all categories for that card

### Excluded Categories

Modify the `excluded_categories` list in `config.json` to skip certain expense types:

```json
{
  "excluded_categories": [
    "Credit Card Payments",
    "Transfers",
    "Refunds & Reimbursements"
  ]
}
```

## Usage

### Interactive Mode (Recommended for First-Time Users)

```bash
python run.py --interactive
```

This will guide you through all the options with prompts.

### Command-Line Mode

**Dry run (preview only):**
```bash
python run.py --input expenses.csv --dry-run
```

**Process and upload to Splitwise:**
```bash
python run.py --input expenses.csv
```
Note: Uses default group ID 9168077. Override with `--group-id YOUR_ID` if needed.

**Generate summary report only:**
```bash
python run.py --input expenses.csv --summary-only
```

**Custom output file:**
```bash
python run.py --input expenses.csv --output my_expenses.csv --dry-run
```

### Adding Single Transactions

**Interactive transaction entry:**
```bash
python run.py --add-transaction
```
Note: Uses default group ID 9168077. Override with `--group-id YOUR_ID` if needed.

This will prompt you for:
- Date (defaults to today)
- Description
- Category
- Amount
- Card/Account (optional, for cashback calculation)

**Quick add via command line:**
```bash
python run.py --transaction-description "Dinner at Restaurant" \
              --transaction-category "Restaurants" \
              --transaction-amount 45.50 \
              --transaction-account "Savor - Ending in 9209"
```
Note: Uses default group ID 9168077. Override with `--group-id YOUR_ID` if needed.

**Preview transaction before uploading:**
```bash
python run.py --add-transaction --dry-run
```

### Command-Line Options

```
--input, -i          Path to input CSV file
--output, -o         Path for output CSV file (optional)
--config, -c         Path to config file (default: config.json)
--group-id, -g       Splitwise group ID (default: 9168077)
--api-key, -k        Splitwise API key (or use env var)
--dry-run, -d        Preview without uploading
--summary-only, -s   Generate report only, don't upload
--interactive, -I    Run in interactive mode
--skip-duplicates    Skip duplicate expenses (default: true)
--verbose, -v        Enable verbose logging

Transaction Mode Options:
--add-transaction, -a           Add a single transaction interactively
--transaction-date              Transaction date (YYYY-MM-DD)
--transaction-description       Transaction description
--transaction-category          Transaction category
--transaction-amount            Transaction amount
--transaction-account           Card/account name (optional)
```

## CSV File Format

Your input CSV file should have these columns:

| Column | Description | Example |
|--------|-------------|---------|
| Date | Transaction date | 03/15/26 or 2026-03-15 |
| Description | Expense description | "Dinner at Restaurant" |
| Category | Expense category | "Restaurants" |
| Amount | Transaction amount (negative for expenses) | -45.50 |
| Account | Card name (must match config.json) | "Savor - Ending in 9209" |

**Example CSV:**
```csv
Date,Description,Category,Amount,Account
03/15/26,Grocery Store,Groceries,-125.50,Savor - Ending in 9209
03/16/26,Restaurant Dinner,Restaurants,-65.00,Citi Custom Cash Card - Ending in 9673
```

## Output Files

The application generates several output files:

1. **Modified CSV** (`Modified_<input_filename>.csv`): Processed expenses with cashback applied
2. **Log File** (`expense_tracker_YYYYMMDD_HHMMSS.log`): Detailed operation log
3. **Summary JSON** (optional): Statistics in JSON format

## Example Workflow

### Monthly Expense Processing

1. **Export your expenses** from your bank/credit card as CSV
2. **Run in dry-run mode** to preview:
   ```bash
   python run.py --input march_expenses.csv --dry-run
   ```
3. **Review the summary** to ensure everything looks correct
4. **Upload to Splitwise**:
   ```bash
   python run.py --input march_expenses.csv --group-id 12345
   ```
5. **Check the log file** if any issues occurred

### Adding a New Credit Card

1. Open `config.json`
2. Add your card under the `"cards"` section:
   ```json
   "New Card - Ending in 5678": {
     "categories": {
       "Dining": 0.04,
       "Gas": 0.03
     },
     "default_cashback": 0.01
   }
   ```
3. Save the file - no code changes needed!

### Updating Cashback Rates

When your card's cashback rates change:

1. Open `config.json`
2. Find your card
3. Update the cashback rates
4. Save - changes take effect immediately

### Quick Transaction Entry

For one-off expenses you want to add immediately:

1. **Interactive mode** (recommended for first-time):
   ```bash
   python run.py --add-transaction
   ```
   Follow the prompts to enter transaction details

2. **Command-line mode** (for scripting or quick entry):
   ```bash
   python run.py --transaction-description "Lunch" \
                 --transaction-category "Restaurants" \
                 --transaction-amount 25.00
   ```

3. **With cashback calculation**:
   ```bash
   python run.py --add-transaction \
                 --transaction-account "Savor - Ending in 9209"
   ```
   The system will automatically apply the correct cashback rate based on your card and category configuration

**Note:** All commands use the default group ID 9168077. To use a different group, add `--group-id YOUR_ID` to any command.

## Troubleshooting

### "Missing required environment variables"

**Solution:** Create a `.env` file or set environment variables:
```bash
export SPLITWISE_API_KEY="your_key_here"
export SPLITWISE_GROUP_ID="12345"
```

### "Card not found in configuration"

**Solution:** Add your card to `config.json` with the exact name as it appears in your CSV file.

### "File not found"

**Solution:** Check that your file paths are correct. Use absolute paths if relative paths don't work:
```bash
python run.py --input /full/path/to/expenses.csv
```

### Expenses not uploading

**Solution:** 
1. Check your API key is valid
2. Verify your group ID is correct
3. Check the log file for detailed error messages
4. Try dry-run mode first to see if expenses are being processed

### Duplicate expenses

**Solution:** The application automatically detects duplicates within a session. If you need to re-upload, the duplicate detection will prevent double-posting.

## Advanced Features

### Custom Logging

Control log verbosity:
```bash
python run.py --input expenses.csv --verbose
```

### Batch Processing

Process multiple months:
```bash
for file in expenses_*.csv; do
    python run.py --input "$file" --group-id 12345
done
```

### Summary Reports

Generate detailed JSON reports:
```python
from expense_tracker import save_summary_json
# Summary is automatically saved during processing
```

## Project Structure

```
SplitWiseProject/
├── config.json              # Card and cashback configuration
├── .env.example            # Environment variable template
├── README.md               # This file
├── run.py                  # Main entry point
├── cli.py                  # Command-line interface
├── logger.py               # Logging configuration
├── config_loader.py        # Configuration management
├── expense_tracker.py      # Expense processing logic
├── splitwise_client.py     # Splitwise API client
├── add_transaction.py      # Single transaction handling
├── main.py                 # Legacy entry point (deprecated)
├── expenses.py             # Legacy module (deprecated)
└── splitwise.py            # Legacy module (deprecated)
```

## Migration from Old Version

If you were using the old `main.py`:

**Old way:**
```bash
export CSV_READ_PATH=/path/to/expenses/
export CSV_READ_FILE_NAME=expenses.csv
python main.py
```

**New way:**
```bash
python run.py --input /path/to/expenses/expenses.csv --group-id 12345
```

The new version offers:
- Better error handling
- Dry run mode
- Duplicate detection
- Summary reports
- Interactive mode
- Easier configuration

## Contributing

Feel free to submit issues or pull requests to improve this tool!

## License

This project is for personal use. Modify as needed for your own expense tracking needs.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the log files for detailed error messages
3. Ensure your `config.json` is properly formatted
4. Verify your environment variables are set correctly

---

**Happy expense tracking! 💰**