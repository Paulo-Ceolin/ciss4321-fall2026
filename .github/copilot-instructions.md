# Expense Tracker Core - Repository Rules & Directives
# Target Python Version: 3.11+
 
## 1. Domain Types & Precision (CRITICAL)
- NEVER use standard Python `float` for currency calculations, splits, or balances.
- ALWAYS use `decimal.Decimal` with explicit rounding strategies to avoid cent loss.
- In `split_expense`:
  - The sum of all allocated split amounts MUST exactly equal `original_expense.amount`.
  - Distribute any remainder cents (e.g. from 100.00 / 3 = 33.33 each with 0.01 leftover) deterministically to the first participant.
- Preserve explicit enum typing using `tracker.models.Category`. Never substitute raw strings for categories.
 
## 2. Architecture & Persistence Contracts
- NEVER read or write directly to local disk files from inside `service.py` or `reports.py`.
- ALWAYS route all persistence and data retrieval through `StorageInterface` defined in `tracker.storage`.
- In `ExpenseService`:
  - Always verify that user IDs (`paid_by`, split participants) exist via `self.storage.get_user(uid)` before committing records.
  - Raise `ValueError` with clear messages when foreign entities do not exist.
- In `ReportService`:
  - Fetch expenses exclusively via `self.storage.list_expenses()`. Filter in-memory or query through storage.
 
## 3. Data Ingestion & Boundaries
- When parsing external inputs (e.g. CSV, JSON, form dictionaries):
  - Parse and validate raw data directly into `tracker.models.Expense` instances before storing.
  - Convert date strings to `datetime.date` using `date.fromisoformat`.
  - Convert amount strings directly to `Decimal(val)` (e.g. `Decimal("42.50")`).
 Do NOT do `Decimal(float(val))`.
 
## 4. Code Quality, Typing & Linting
- Maintain 100% type annotation coverage on all functions, parameters, and return types.
- Strict `mypy` compliance is required: 0 untyped defs, 0 `Any` leaks, and 0 bare exceptions.
- Never write bare `except:`; catch specific exceptions (`ValueError`, `KeyError`, `ValidationError`).
- Follow PEP 8 via `ruff` with 88-character line limits.
