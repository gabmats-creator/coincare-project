from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Bill:
    _id: str
    billName: str
    billValue: float
    expireDate: str
    description: str
    insertDate: str

@dataclass
class User:
    _id: str
    email: str
    password: str
    bills: list[str] = field(default_factory=list)