# Post-Mortem: The Naive Prompting Experiment

This report summarizes the issues revealed by the AI-generated implementation and the repository’s validation checks.

## 1. Precision & Types

The codebase uses `Decimal` for currency values instead of `float` or integer cents. In `src/tracker/models.py`, both `Expense.amount` and `SplitAllocation.amount` are defined as `Decimal`, which is the correct type for precise money handling.

If $100.00 is split among 3 people, a naive `float`-based approach will produce repeating decimal values such as `33.333333...`. That causes rounding drift and can make the final total not exactly equal to $100.00. A correct split should allocate cents precisely, such as:

- $33.33
- $33.33
- $33.34

This preserves the exact total of $100.00 and avoids fractional-cent errors.

## 2. Architectural Drift

The architecture remains aligned with the project design: both `ExpenseService` and `ReportService` depend on `StorageInterface`, and the implementation of persistence lives in `src/tracker/storage.py`.

This is the intended abstraction boundary. There is no evidence that the service or report layers read or wrote files directly. The design correctly routes storage access through the interface instead of embedding file I/O in business logic.

## 3. Contracts & Validation

The correct pattern is to build validated `Expense` models before saving them. In `src/tracker/models.py`, `Expense`, `User`, and `SplitAllocation` are Pydantic models with validation rules such as positive amounts and 2-decimal currency precision.

A CSV importer should parse each row, validate it into a proper `Expense` object, and only then persist it. For example, the importer should convert raw CSV data into `Expense(**row)` or `Expense.model_validate(row)` before storing it. This prevents invalid data from reaching storage without enforcement.

## 4. Code Quality Findings

I verified the project with the repository’s lint and type checks:

- `ruff check .` reported issues such as:
  - unsorted imports
  - deprecated `typing.Dict`, `typing.List`, and `typing.Optional`
  - unnecessary imports
  - style problems that prefer `list[...]`, `dict[...]`, and `T | None`

- `mypy src` reported: `Success: no issues found in 5 source files`

This means the AI-generated code passed strict type checking, but it still failed the project’s linting standards and modern Python typing conventions. The problem was not fundamentally a typing bug; it was inconsistent code quality and outdated style.

## 5. Repository Rules That Would Have Prevented These Issues

The following three rules would have prevented the main pitfalls seen in this experiment:

1. `Never use float for money; use Decimal for all currency values and exact split calculations.`
2. `All business logic must depend on StorageInterface; never perform direct file I/O in service.py or reports.py.`
3. `Parse and validate all CSV and JSON input into Pydantic models before storage; reject invalid data before it reaches the database or in-memory store.`

A stronger `.cursorrules` example would be:

```text
- Use Decimal for all financial values; never use float for expense totals or splits.
- Keep persistence behind StorageInterface; do not perform direct file I/O in app services.
- Parse external data into validated Pydantic models before saving to storage.
- Prefer modern Python typing: list[T], dict[K, V], and T | None.
- Keep imports sorted and remove unused imports.
```

These rules directly address the main failure modes in the naive prompting experiment: exact money handling, architectural boundaries, and contract validation.
