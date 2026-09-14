from decimal import Decimal, ROUND_DOWN
from typing import List, Optional

from tracker.models import Expense
from tracker.storage import StorageInterface


class ExpenseService:
    """Core service orchestrating expense operations and business rules."""

    def __init__(self, storage: StorageInterface) -> None:
        self.storage = storage

    def record_expense(self, expense: Expense) -> None:
        """Record a single expense after validating the payer exists."""
        payer = self.storage.get_user(expense.paid_by)
        if payer is None:
            raise ValueError(f"User {expense.paid_by} does not exist.")
        self.storage.save_expense(expense)

    def split_expense(
        self,
        original_expense_id: str,
        target_user_ids: List[str],
        percentages: Optional[List[Decimal]] = None,
    ) -> List[Expense]:
        """Split an expense into cent-accurate expenses and store them."""
        original = self.storage.get_expense(original_expense_id)
        if original is None:
            raise ValueError(f"Expense {original_expense_id} does not exist.")
        if not target_user_ids:
            raise ValueError("At least one target user is required.")
        for user_id in target_user_ids:
            if self.storage.get_user(user_id) is None:
                raise ValueError(f"User {user_id} does not exist.")

        if percentages is not None:
            if len(percentages) != len(target_user_ids):
                raise ValueError("Percentages must match the target user count.")
            if any(percentage <= 0 for percentage in percentages):
                raise ValueError("Percentages must be greater than zero.")
            if sum(percentages, Decimal("0")) != Decimal("100"):
                raise ValueError("Percentages must total 100.")
            exact_amounts = [
                original.amount * percentage / Decimal("100")
                for percentage in percentages
            ]
        else:
            share = original.amount / Decimal(len(target_user_ids))
            exact_amounts = [share] * len(target_user_ids)

        cent = Decimal("0.01")
        amounts = [amount.quantize(cent, rounding=ROUND_DOWN) for amount in exact_amounts]
        remainder = original.amount - sum(amounts, Decimal("0"))
        amounts[0] += remainder

        split_expenses: List[Expense] = []
        for index, (user_id, amount) in enumerate(zip(target_user_ids, amounts)):
            split_expense = original.model_copy(
                update={
                    "expense_id": f"{original.expense_id}-split-{index + 1}",
                    "amount": amount,
                    "paid_by": user_id,
                    "split_group_id": original.expense_id,
                }
            )
            self.storage.save_expense(split_expense)
            split_expenses.append(split_expense)
        return split_expenses