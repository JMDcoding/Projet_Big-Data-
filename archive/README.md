# 📦 Archive - Test & Utility Files

This folder contains all test, verification, and deprecated files that are no longer used in the main project but kept for reference and learning purposes.

## 📁 Folder Structure

### `tests/` - Test and Verification Scripts
Contains scripts used to test and verify functionality during development:
- `check_*.py` - Data verification scripts
- `test_*.py` - Test scripts
- `verify_*.py` - Verification and validation scripts

**Example files:**
- `check_schema.py` - Verify database schema
- `test_db.py` - Test database connections
- `verify_demo_data.py` - Verify demo data was loaded correctly

**When to use:** Reference these if you need to understand how to validate specific components.

---

### `utilities/` - Data Fetching and Loading Scripts
Contains scripts for fetching data and populating the database (now in `scripts/` folder):
- `fetch_*.py` - External API data fetchers
- `populate_*.py` - Data loading scripts
- `insert_*.py` - Direct database insertion utilities
- `refresh_*.py` - Data refresh orchestration
- `regenerate_*.py` - Data regeneration utilities
- `reset_*.py` - Data clearing scripts

**These are now in `scripts/` as production entry points:**
- Use `scripts/refresh_data.py` instead of `fetch_*.py`
- Use `scripts/populate_demo.py` instead of `populate_*.py`
- Use `scripts/reset_data.py` instead of `reset_*.py`

**When to use:** Reference these if you need to understand how data operations work.

---

### `setup-scripts/` - Configuration and Setup
Contains batch and PowerShell scripts for environment setup (now in `scripts/`):
- `*.bat` files - Windows batch setup scripts
- `*.ps1` files - PowerShell setup scripts

**These are now handled directly by:**
- `scripts/setup_database.py` - Use this for database initialization
- `README.md` - Quickstart guide (in root)

**When to use:** Reference if you need to understand the original setup process.

---

### `deprecated/` - Old Code and Documentation
Contains deprecated files no longer used:
- `main.py`, `main_fixed.py` - Old application entry points (replaced by `app.py`)
- `README_*.md` - Old documentation (consolidated into `README.md`)
- Configuration files and old imports
- Output files and logs

**When to use:** Reference only if you need to understand the history of the project.

---

## 🎯 How to Use This Archive

### As a Developer:
You should **rarely need** files from this archive. The main application uses:
- `../app.py` - Main Streamlit dashboard
- `../scripts/` - Utility scripts for data operations
- `../src/` - Core application code

### For Understanding:
If you want to understand how a feature works:
1. Check the main code in `../src/`
2. If not clear, look at corresponding test in `archive/tests/`
3. If data operations, check `archive/utilities/` or better yet: `../scripts/`

### For Extending:
When adding new features:
1. Don't copy code from archive
2. Build new code in `../src/` following existing patterns
3. Add tests in `../tests/` using pytest
4. Add utilities in `../scripts/` if needed

---

## 📊 Archive Contents Summary

| Category | Files | Status | Replacement |
|----------|-------|--------|-------------|
| tests/ | 985+ | ✗ Archived | Use `/pytest` tests instead |
| utilities/ | 18 | ✗ Archived | Use `scripts/` folder instead |
| setup-scripts/ | 13 | ✗ Archived | Use automated `scripts/` instead |
| deprecated/ | 14+ | ✗ Archived | Use current implementations |
| **TOTAL** | **1030+** | Organized and preserved | |

---

## 🚀 If You Need Something From Here

**Scenario 1:** "I need to understand database testing"
→ Check `tests/test_db.py` in this archive
→ Then write your own test in `/tests` using pytest

**Scenario 2:** "I need to fetch data from an API"
→ Check `utilities/fetch_*.py` to understand the pattern
→ Use `scripts/refresh_data.py` for actual operations

**Scenario 3:** "I need to set up the database"
→ Don't use old setup-scripts
→ Use `scripts/setup_database.py` instead

**Scenario 4:** "I want to understand old code"
→ Check `deprecated/main.py` for reference
→ But use `app.py` for the actual application

---

## 🧹 Cleanup Notes

This archive was created as part of project reorganization in **Session 8**:
- **Removed:** 60+ test/demo files from project root
- **Organized:** Into 4 categories (tests, utilities, setup-scripts, deprecated)
- **Kept:** Only essential production files in root
- **Result:** Clean, focused project structure

---

## ⚠️ Important

**Do NOT:**
- Delete files from this archive without backup
- Use old scripts from here in production
- Copy code from archived files without review
- Assume archived files are current/correct

**DO:**
- Reference archived files for understanding
- Use current implementations in main project
- Write new code in `src/` or `scripts/`
- Keep this archive as historical reference

---

**Last Updated:** Session 8 - Project Reorganization
**Status:** Clean project structure achieved ✅

