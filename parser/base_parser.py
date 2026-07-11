from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import BinaryIO

from model.transaction import Transaction


class ParserProviders(str, Enum):
    FINECO = "fineco"

class BaseParser(ABC):

    SUPPORTED_EXTENSIONS: set[str] = set()

    def validate_extension(self, filename: str) -> None:
        ext = Path(filename).suffix.lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"{self.__class__.__name__} does not support extension '{ext}'")

    @abstractmethod
    def parse(self, filename: str, source: BinaryIO) -> list[Transaction]:
        """
        Process the input source and return a list of Transaction objects.
        """
        ...