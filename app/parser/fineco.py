from typing import BinaryIO

import pandas as pd

from model.transaction import Transaction
from model.portfolio import PortfolioMovement, PortfolioSnapshot
from parser.base_parser import BaseParser


class FinecoParser(BaseParser):

    @staticmethod
    def _parse_liquidity_movements_xlsx(source: BinaryIO) -> list[Transaction]:
        df_raw = pd.read_excel(source, header=None, sheet_name="Movimenti")

        # Locate the header row by finding the row that contains "Data_Operazione"
        header_row = df_raw[df_raw.apply(lambda r: r.astype(str).str.contains("Data_Operazione").any(), axis=1)].index[0]

        df = df_raw.iloc[header_row + 1:].copy()
        df.columns = df_raw.iloc[header_row].tolist()
        df = df.reset_index(drop=True)

        df = df[df["Stato"] == "Contabilizzato"]
        df = df.dropna(subset=["Data_Operazione", "Data_Valuta"], how="any")

        df["amount"] = df["Entrate"].fillna(0) + df["Uscite"].fillna(0)
        df = df[df["amount"] != 0]

        return [
            Transaction(
                value_date=pd.Timestamp(row["Data_Valuta"]).date(),
                accounting_date=pd.Timestamp(row["Data_Operazione"]).date(),
                amount=row["amount"],
                description=f"{row['Descrizione']} - {row['Descrizione_Completa']}"
            )
            for _, row in df.iterrows()
        ]

    
    @staticmethod
    def _parse_portfolio_snapshot_xlsx(source: BinaryIO) -> list[PortfolioSnapshot]:
        df_raw = pd.read_excel(source, header=2)
        
        df = df_raw
        df.dropna(inplace=True)

        return [
            PortfolioSnapshot(
                isin=row['ISIN'],
                invested_capital=row['Valore di carico'],
                market_value=row['Valore di mercato €']
            )
            for _, row in df.iterrows()
        ]

    @staticmethod
    def _parse_portfolio_movements_xlsx(source: BinaryIO) -> list[PortfolioMovement]:
        df = pd.read_excel(source, header=5)
        df.dropna(inplace=True)

        return [
            PortfolioMovement(
                title=row["Titolo"],
                isin=row["Isin"],
                value_date=row['Data valuta'],
                accounting_date=row['Operazione'],
                movement_type=row['Segno'],
                unit_price=row['Prezzo'],
                quantity=row['Quantita'],
                exchange_rate=row['Cambio'],
                invested_capital=row['Controvalore'])
            for _, row in df.iterrows()
        ]


    
    SUPPORTED_LIQUIDITY_MOVEMENTS_EXTENSIONS = {".xlsx": _parse_liquidity_movements_xlsx,
                                                 ".xls": _parse_liquidity_movements_xlsx}
    SUPPORTED_PORTFOLIO_SNAPSHOT_EXTENSIONS = {".xlsx": _parse_portfolio_snapshot_xlsx,
                                                ".xls": _parse_portfolio_snapshot_xlsx}
    SUPPORTED_PORTFOLIO_MOVEMENTS_EXTENSIONS = {".xlsx": _parse_portfolio_movements_xlsx,
                                                ".xls": _parse_portfolio_movements_xlsx}