import hashlib
import json
from datetime import date, datetime
from uuid import uuid4

from pydantic import BaseModel, Field, computed_field


class Transaction(BaseModel):
    uid: str = Field(default_factory=lambda: str(uuid4()))
    value_date: date
    accounting_date: date
    amount: float
    description: str


class TransactionDTO(Transaction):
    category: str | None = None
    upload_datetime: datetime = Field(default_factory=datetime.now)

    @classmethod
    def from_transaction(cls, transaction: Transaction, **kwargs) -> "TransactionDTO":
        return cls(**transaction.model_dump(), **kwargs)

    @computed_field
    @property
    def digest(self) -> str:
        payload = self.model_dump(mode="python", exclude={"uid", "digest", "upload_datetime", "category"})
        payload.pop("digest", None)
        serialized = json.dumps(payload, default=str, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()