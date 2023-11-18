from dataclasses import dataclass, field

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
    bills: list[str] = field(default_factory=list)
    receipts: list[str] = field(default_factory=list)

@dataclass
class Receipt:
    _id: str
    receiptName: str
    receiptValue: float
    insertDate: str
    description: str
    insertMonth: str