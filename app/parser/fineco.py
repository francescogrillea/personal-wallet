from typing import BinaryIO

import pandas as pd

from app.model.transaction import Transaction
from app.parser.base_parser import BaseParser


class FinecoParser(BaseParser):

    def _parse_xlsx(source: BinaryIO) -> list[Transaction]:
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

    SUPPORTED_EXTENSIONS = {".xlsx": _parse_xlsx}