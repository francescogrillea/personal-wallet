from datetime import date
import hashlib
import json
from uuid import uuid4
from datetime import date, datetime

from pydantic import BaseModel, Field, computed_field, field_validator

class PortfolioMovement(BaseModel):
    uid: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    isin: str
    value_date: date
    accounting_date: date
    movement_type: str
    unit_price: float
    quantity: float
    exchange_rate: float
    invested_capital: float

    @field_validator("unit_price", "quantity", "exchange_rate", "invested_capital", mode="before")
    @classmethod
    def parse_custom_float(cls, value):
        if isinstance(value, str):
            return float(value.replace(".", "").replace(",", "."))
        return value


    @field_validator("value_date", "accounting_date", mode="before")
    @classmethod
    def parse_custom_date(cls, value):
        if isinstance(value, str):
            return datetime.strptime(value, "%d/%m/%Y").date()
        return value

class PortfolioMovementDTO(PortfolioMovement):
    
    upload_datetime: datetime = Field(default_factory=datetime.now)
    
    # @field_validator('invested_capital', 'market_value', mode='after')
    # @classmethod
    # def round_floats(cls, value: float) -> float:
    #     return round(value, 2)
    
    @classmethod
    def from_value_to_dto(cls, movements: PortfolioMovement, **kwargs) -> "PortfolioMovementDTO":
        return cls(**movements.model_dump(), **kwargs)
    
    @computed_field
    @property
    def digest(self) -> str:
        payload = self.model_dump(mode="python", exclude={"uid", "digest", "upload_datetime"})
        payload.pop("digest", None)
        serialized = json.dumps(payload, default=str, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()
    

class PortfolioSnapshot(BaseModel):
    upload_date: date = Field(default_factory=date.today)
    isin: str
    invested_capital: float
    market_value: float


class PortfolioSnapshotDTO(PortfolioSnapshot):
    
    @field_validator('invested_capital', 'market_value', mode='after')
    @classmethod
    def round_floats(cls, value: float) -> float:
        return round(value, 2)
    
    @classmethod
    def from_value_to_dto(cls, portfolio: PortfolioSnapshot, **kwargs) -> "PortfolioSnapshotDTO":
        return cls(**portfolio.model_dump(), **kwargs)