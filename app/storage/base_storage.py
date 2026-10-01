from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from pydantic import BaseModel

from model.transaction import TransactionDTO
from model.portfolio import PortfolioMovementDTO, PortfolioSnapshotDTO


class StorageProviders(str, Enum):
    GOOGLE_SHEETS = "google_sheets"    

class BaseStorageResponse(BaseModel):
    status: str
    items_saved: int
    error_message: str | None = None

class BaseStorage(ABC):
    
    @abstractmethod
    def convert_liquidity_movements(self, data: list[TransactionDTO]) -> Any:
        pass
    
    @abstractmethod
    def save_liquidity_movements(self, data: list[TransactionDTO]) -> BaseStorageResponse:
        pass
    
    @abstractmethod
    def convert_portfolio_snapshot(self, data: list[PortfolioSnapshotDTO]) -> Any:
        pass

    @abstractmethod
    def save_portfolio_snapshot(self, data: list[PortfolioSnapshotDTO]) -> BaseStorageResponse:
        pass
    
    @abstractmethod
    def convert_portfolio_movements(self, data: list[PortfolioMovementDTO]) -> Any:
        pass
    
    @abstractmethod
    def save_portfolio_movements(self, data: list[PortfolioMovementDTO]) -> BaseStorageResponse:
        pass

    @abstractmethod
    def load(self) -> list[TransactionDTO]:
        pass