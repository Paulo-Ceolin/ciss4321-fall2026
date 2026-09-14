import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from tracker.models import Category, Expense


def read_expenses_from_csv(filepath: str | Path) -> list[Expense]:
    """Parse and validate expenses from a CSV file."""
    required_columns = {"date", "amount", "category", "description", "paid_by"}
    expenses: list[Expense] = []

    with Path(filepath).open(newline="", encoding="utf-8") as csv_file:
        reader = csv.reader(csv_file)
        try:
            headers = next(reader)
        except StopIteration as error:
            raise ValueError("CSV file is empty.") from error

        missing_columns = required_columns - set(headers)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"CSV is missing required columns: {missing}.")

        column_indexes = {header: headers.index(header) for header in required_columns}
        for row_number, row in enumerate(reader, start=2):
            if not row or all(not value.strip() for value in row):
                continue
            if len(row) < len(headers):
                raise ValueError(f"CSV row {row_number} has too few columns.")

            try:
                expenses.append(
                    Expense(
                        expense_id=f"csv-{row_number}",
                        amount=Decimal(row[column_indexes["amount"]]),
                        category=Category(row[column_indexes["category"]]),
                        description=row[column_indexes["description"]],
                        date=date.fromisoformat(row[column_indexes["date"]]),
                        paid_by=row[column_indexes["paid_by"]],
                    )
                )
            except (IndexError, InvalidOperation, ValueError) as error:
                raise ValueError(f"Invalid expense data on CSV row {row_number}.") from error

    return expenses