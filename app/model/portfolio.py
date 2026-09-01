from datetime import date

from pydantic import BaseModel, Field, field_validator

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