from abc import ABC, abstractmethod
from enum import Enum

from pydantic import BaseModel

from model.transaction import TransactionDTO
from model.portfolio import PortfolioSnapshotDTO


class StorageProviders(str, Enum):
    GOOGLE_SHEETS = "google_sheets"    

class BaseStorageResponse(BaseModel):
    status: str
    items_saved: int
    error_message: str | None = None

class BaseStorage(ABC):
    @abstractmethod
    def save_transactions(self, data: list[TransactionDTO]) -> BaseStorageResponse:
        pass

    @abstractmethod
    def save_portfolio(self, data: list[PortfolioSnapshotDTO], sheet_name: str, cell: str) -> BaseStorageResponse:
        pass

    @abstractmethod
    def load(self) -> list[TransactionDTO]:
        pass