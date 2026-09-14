from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Category(str, Enum):
    FOOD = "food"
    TRANSPORT = "transport"
    UTILITIES = "utilities"
    ENTERTAINMENT = "entertainment"
    OTHER = "other"


class User(BaseModel):
    user_id: str
    name: str
    email: str


class Expense(BaseModel):
    expense_id: str
    amount: Decimal = Field(gt=Decimal("0.00"), decimal_places=2)
    category: Category
    description: str
    date: date
    paid_by: str
    split_group_id: Optional[str] = None


class SplitAllocation(BaseModel):
    user_id: str
    amount: Decimal = Field(gt=Decimal("0.00"), decimal_places=2)