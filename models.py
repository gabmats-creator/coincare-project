from dataclasses import dataclass, field
from typing import List

@dataclass
class Bill:
    _id: str
    billName: str
    billValue: float
    expireDate: str
    description: str
    insertDate: str
    insertMonth: str
    mensal: bool

@dataclass
class User:
    _id: str
    name: str
    email: str
    income: float
    password: str
    reset_token: str
    bills: List[str] = field(default_factory=list)
    receipts: List[str] = field(default_factory=list)

@dataclass
class Receipt:
    _id: str
    receiptName: str
    receiptValue: float
    insertDate: str
    description: str
    insertMonth: str

@dataclass
class Access:
    _id: str
    logged_access: int
    general_access: int
    current_session: str