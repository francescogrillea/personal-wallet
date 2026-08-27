from abc import ABC
from enum import Enum
from pathlib import Path
from typing import BinaryIO, Callable

from model.transaction import Transaction


class ParserProviders(str, Enum):
    FINECO = "fineco"

class BaseParser(ABC):

    SUPPORTED_EXTENSIONS: dict[str, Callable[[BinaryIO], list[Transaction]]] = {}

    def __init__(self):
        raise TypeError(f"{self.__class__.__name__} è una classe statica e non può essere istanziata.")

    @classmethod
    def parse(cls, filename: str, source: BinaryIO) -> list[Transaction]:
        ext = Path(filename).suffix.lower()
        handler = cls.SUPPORTED_EXTENSIONS.get(ext)
        if handler is None:
            raise ValueError(f"{cls.__name__} does not support extension '{ext}'")
        return handler(source)