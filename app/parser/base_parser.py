from enum import Enum
from pathlib import Path
from typing import BinaryIO, Callable

from model.portfolio import PortfolioMovement, PortfolioSnapshot
from model.transaction import Transaction


class ParserProviders(str, Enum):
    FINECO = "fineco"

class BaseParser:

    SUPPORTED_LIQUIDITY_MOVEMENTS_EXTENSIONS: dict[str, Callable[[BinaryIO], list[Transaction]]] = {}
    SUPPORTED_PORTFOLIO_MOVEMENTS_EXTENSIONS: dict[str, Callable[[BinaryIO], list[Transaction]]] = {}
    SUPPORTED_PORTFOLIO_SNAPSHOT_EXTENSIONS: dict[str, Callable[[BinaryIO], list[PortfolioSnapshot]]] = {}


    def __init__(self):
        raise TypeError(f"{self.__class__.__name__} è una classe statica e non può essere istanziata.")

    @classmethod
    def _parse_file(cls, filename: str, source: BinaryIO, extensions: dict[str, Callable[[BinaryIO], list[Transaction]]]) -> list[Transaction]:
        ext = Path(filename).suffix.lower()
        handler = extensions.get(ext)
        if handler is None:
            raise ValueError(f"{cls.__name__} does not support extension '{ext}'")
        return handler(source)

    @classmethod
    def parse_liquidity_movements_file(cls, filename: str, source: BinaryIO) -> list[Transaction]:
        return cls._parse_file(filename, source, cls.SUPPORTED_LIQUIDITY_MOVEMENTS_EXTENSIONS)

    @classmethod
    def parse_portfolio_snapshot_file(cls, filename: str, source: BinaryIO) -> list[PortfolioSnapshot]:
        return cls._parse_file(filename, source, cls.SUPPORTED_PORTFOLIO_SNAPSHOT_EXTENSIONS)
    
    @classmethod
    def parse_portfolio_movements_file(cls, filename: str, source: BinaryIO) -> list[PortfolioMovement]:
        return cls._parse_file(filename, source, cls.SUPPORTED_PORTFOLIO_MOVEMENTS_EXTENSIONS)
        