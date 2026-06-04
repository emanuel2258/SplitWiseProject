# 🚀 Quick Start Guide

## What is this project?
Automated expense tracking system that processes CSV files from Empower, calculates cashback, and uploads to Splitwise.

---

## 📋 First Time Setup (One-time)

1. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Your configuration is already set up:**
   - ✅ `.env` - API keys and paths configured
   - ✅ `config.json` - Card cashback rates configured

---

## 🎯 How to Use (Choose One)

### Option 1: Process Latest Transactions (Easiest) ⭐
```bash
python3 process_monthly.py
```
Automatically finds and processes your most recent transaction file.

### Option 2: Process Specific File
```bash
python3 run.py --input "path/to/transactions.csv" --dry-run
```
Preview first, then remove `--dry-run` to upload.

### Option 3: Add Single Transaction
```bash
python3 add_transaction.py
```
For quick one-off expenses.

---

## 📁 Project Organization

```
Root Directory (You are here!)
├── run.py                  ⭐ Main program
├── process_monthly.py      🔄 Auto-find latest file
├── add_transaction.py      ➕ Add single expense
├── config.json             ⚙️  Card settings
├── .env                    🔐 API keys (configured)
│
├── src/                    📦 Source code (don't touch)
│   ├── core/              
│   └── utils/             
│
├── docs/                   📖 Documentation
├── legacy/                 🗄️  Old files (ignore)
└── logs/                   📝 Auto-generated logs
```

---

## 🔧 Common Tasks

### Update Cashback Rates
1. Open `config.json`
2. Find your card
3. Update percentage (e.g., `0.03` = 3%)
4. Save - changes apply immediately

### Add New Card
1. Open `config.json`
2. Copy existing card format
3. Add your new card details
4. Save

### View Logs
```bash
tail -f logs/expense_tracker_*.log
```

---

## 📚 Need More Help?

- **Full Documentation:** [`README.md`](README.md)
- **Project Structure:** [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md)
- **Migration Guide:** [`docs/MIGRATION_GUIDE.md`](docs/MIGRATION_GUIDE.md)

---

## ⚡ Quick Commands Reference

| Task | Command |
|------|---------|
| Process latest file | `python3 process_monthly.py` |
| Dry run specific file | `python3 run.py --input "file.csv" --dry-run` |
| Upload to Splitwise | `python3 run.py --input "file.csv"` |
| Add single transaction | `python3 add_transaction.py` |
| Interactive mode | `python3 run.py --interactive` |
| View help | `python3 run.py --help` |

---

## ✅ Your Current Setup

- **Transaction Files:** `../../empower_data/Transactions/`
- **Output Files:** `../../empower_data/Generated/`
- **Splitwise Group ID:** 9168077
- **API Key:** Configured in `.env`

Everything is ready to go! Just run `python3 process_monthly.py` to get started.

---

## 🆘 Troubleshooting

**Problem:** "Module not found"  
**Solution:** Run `pip3 install -r requirements.txt`

**Problem:** "File not found"  
**Solution:** Check paths in `.env` file

**Problem:** "API error"  
**Solution:** Verify API key in `.env` is correct

For more help, check the logs in `logs/` directory.