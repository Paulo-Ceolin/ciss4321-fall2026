from decimal import Decimal
from typing import TypedDict

from tracker.models import Category
from tracker.storage import StorageInterface


class MonthlyReport(TypedDict):
    total_spending: Decimal
    spending_by_category: dict[Category, Decimal]
    top_category: Category | None


class ReportService:
    """Generates summaries and spending metrics."""

    def __init__(self, storage: StorageInterface) -> None:
        self.storage = storage

    def generate_monthly_report(self, year: int, month: int) -> MonthlyReport:
        """Return spending totals for the requested calendar month."""
        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12.")

        spending_by_category: dict[Category, Decimal] = {}
        total_spending = Decimal("0.00")

        for expense in self.storage.list_expenses():
            if expense.date.year != year or expense.date.month != month:
                continue
            total_spending += expense.amount
            spending_by_category[expense.category] = (
                spending_by_category.get(expense.category, Decimal("0.00"))
                + expense.amount
            )

        top_category = (
            max(spending_by_category, key=spending_by_category.__getitem__)
            if spending_by_category
            else None
        )
        return {
            "total_spending": total_spending,
            "spending_by_category": spending_by_category,
            "top_category": top_category,
        }