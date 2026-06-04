# Quick Start: Adding Single Transactions

This guide shows you how to quickly add individual transactions to Splitwise without needing a CSV file.

## Prerequisites

1. Set up your environment variables (`.env` file):
   ```bash
   SPLITWISE_API_KEY=your_api_key_here
   SPLITWISE_GROUP_ID=your_group_id_here
   ```

2. Configure your cards in `config.json` for automatic cashback calculation

## Usage Examples

### 1. Interactive Mode (Recommended for First-Time Users)

```bash
python3 run.py --add-transaction
```

**Note:** Uses default group ID 9168077. Override with `--group-id YOUR_ID` if needed.

You'll be prompted for:
- **Date**: Press Enter for today, or enter in YYYY-MM-DD or MM/DD/YY format
- **Description**: What you spent money on (e.g., "Dinner at Italian Restaurant")
- **Category**: Expense category (e.g., "Restaurants", "Groceries", "Entertainment")
- **Amount**: How much you spent (e.g., 45.50)
- **Card**: (Optional) Your card name for cashback calculation

### 2. Quick Add via Command Line

Add a transaction with all details in one command:

```bash
python3 run.py \
  --transaction-description "Dinner at Restaurant" \
  --transaction-category "Restaurants" \
  --transaction-amount 45.50
```

**Note:** Uses default group ID 9168077. Override with `--group-id YOUR_ID` if needed.

### 3. With Cashback Calculation

Include your card name to automatically apply cashback:

```bash
python3 run.py \
  --transaction-description "Grocery Shopping" \
  --transaction-category "Groceries" \
  --transaction-amount 100.00 \
  --transaction-account "Savor - Ending in 9209"
```

If your card has 3% cashback on groceries, the system will automatically calculate:
- Original: $100.00
- Cashback: $3.00 (3%)
- Final amount uploaded: $97.00

### 4. With Custom Date

Add a transaction from a previous date:

```bash
python3 run.py \
  --transaction-description "Coffee Shop" \
  --transaction-category "Restaurants" \
  --transaction-amount 5.75 \
  --transaction-date "2026-05-01"
```

### 5. Preview Before Uploading (Dry Run)

Test your transaction without actually uploading to Splitwise:

```bash
python3 run.py \
  --transaction-description "Test Transaction" \
  --transaction-category "Entertainment" \
  --transaction-amount 25.00 \
  --dry-run
```

## Common Use Cases

### Daily Coffee Purchase
```bash
python3 run.py \
  --transaction-description "Morning Coffee" \
  --transaction-category "Restaurants" \
  --transaction-amount 4.50
```

### Grocery Shopping with Cashback
```bash
python3 run.py \
  --transaction-description "Weekly Groceries" \
  --transaction-category "Groceries" \
  --transaction-amount 150.00 \
  --transaction-account "Savor - Ending in 9209"
```

### Restaurant Dinner
```bash
python3 run.py \
  --transaction-description "Dinner with Friends" \
  --transaction-category "Restaurants" \
  --transaction-amount 85.00 \
  --transaction-account "Citi Custom Cash Card - Ending in 9673"
```

### Gas Station Fill-up
```bash
python3 run.py \
  --transaction-description "Gas Station" \
  --transaction-category "Gasoline/Fuel" \
  --transaction-amount 45.00 \
  --transaction-account "Blue Cash Everyday ( ) - Ending in 1006"
```

**Note:** All examples use the default group ID 9168077. To use a different group, add `--group-id YOUR_ID` to any command.

## Tips

1. **Use Tab Completion**: Most shells support tab completion for long option names
2. **Create Aliases**: Add frequently used commands to your shell's alias file
3. **Dry Run First**: Always test with `--dry-run` when trying new card configurations
4. **Card Names Must Match**: The card name must exactly match what's in your `config.json`
5. **Categories Matter**: Use the same category names as in your config for proper cashback calculation

## Troubleshooting

### "Card not found in configuration"
- Check that your card name exactly matches what's in `config.json`
- Card names are case-sensitive

### "Invalid date format"
- Use YYYY-MM-DD format (e.g., 2026-05-01)
- Or MM/DD/YY format (e.g., 05/01/26)

### "Missing required fields"
- Description, category, and amount are always required
- Date defaults to today if not provided
- Card/account is optional

## Shell Aliases (Optional)

Add these to your `~/.bashrc` or `~/.zshrc` for quick access:

```bash
# Quick transaction add (uses default group ID 9168077)
alias add-expense='python3 /path/to/run.py'

# Add with your most-used card
alias add-expense-savor='python3 /path/to/run.py --transaction-account "Savor - Ending in 9209"'

# For a different group
alias add-expense-other='python3 /path/to/run.py --group-id YOUR_OTHER_GROUP_ID'
```

Then use like:
```bash
add-expense --transaction-description "Lunch" --transaction-category "Restaurants" --transaction-amount 15.00
```

Or with your Savor card:
```bash
add-expense-savor --transaction-description "Dinner" --transaction-category "Restaurants" --transaction-amount 45.00
```

---

**Made with Bob**