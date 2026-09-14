from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from tracker.models import Expense, User


class StorageInterface(ABC):
    @abstractmethod
    def save_expense(self, expense: Expense) -> None:
        pass

    @abstractmethod
    def get_expense(self, expense_id: str) -> Optional[Expense]:
        pass

    @abstractmethod
    def list_expenses(self) -> List[Expense]:
        pass

    @abstractmethod
    def save_user(self, user: User) -> None:
        pass

    @abstractmethod
    def get_user(self, user_id: str) -> Optional[User]:
        pass


class InMemoryStorage(StorageInterface):
    def __init__(self) -> None:
        self._expenses: Dict[str, Expense] = {}
        self._users: Dict[str, User] = {}

    def save_expense(self, expense: Expense) -> None:
        self._expenses[expense.expense_id] = expense

    def get_expense(self, expense_id: str) -> Optional[Expense]:
        return self._expenses.get(expense_id)

    def list_expenses(self) -> List[Expense]:
        return list(self._expenses.values())

    def save_user(self, user: User) -> None:
        self._users[user.user_id] = user

    def get_user(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)