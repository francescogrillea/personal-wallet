import os
from itertools import chain

import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from model.transaction import TransactionDTO
from model.portfolio import PortfolioMovementDTO, PortfolioSnapshotDTO
from storage.base_storage import BaseStorage, BaseStorageResponse

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class GoogleSheetStorageResponse(BaseStorageResponse):
    ...

class GoogleSheetStorage(BaseStorage):

    # def __init__(self, spreadsheet_id: str, range_name: str, *args, **kwargs):
    def __init__(self, *args, **kwargs):
        _credentials = self._load_credentials_from_env()
        _auth = service_account.Credentials.from_service_account_info(_credentials, scopes=SCOPES)

        self.service = build('sheets', 'v4', credentials=_auth)

    @staticmethod
    def _load_credentials_from_env(key_prefix="GOOGLE_SHEET_"):
        """
        Format the environment variables with the specified prefix into a dictionary suitable for service account credentials.
        """

        return {
            key.removeprefix(key_prefix).lower(): value
            for key, value in os.environ.items()
            if key.startswith(key_prefix)
        }

    def load_ids(self, spreadsheet_id: str, sheet: str, cell: str) -> set[str]:
        col, row = ''.join(c for c in cell if c.isalpha()), ''.join(c for c in cell if c.isdigit())
        digest_col = chr(ord(col) + 1)  # digest is the 2nd field
        result = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet}!{digest_col}{row}:{digest_col}"
        ).execute()
        return set(chain.from_iterable(result.get('values', [])))

    
    def convert_liquidity_movements(self, data: list[TransactionDTO]) -> pd.DataFrame:
        
        COLUMNS = ['uid', 'digest', 'upload_datetime', 'value_date', 'accounting_date', 'amount', 'description', 'category']
        df = pd.DataFrame([transaction.model_dump() for transaction in data])[COLUMNS]
        df['value_date'] = df['value_date'].apply(lambda x: x.strftime('%d/%m/%Y'))
        df['accounting_date'] = df['accounting_date'].apply(lambda x: x.strftime('%d/%m/%Y'))
        df['upload_datetime'] = df['upload_datetime'].apply(lambda x: x.strftime('%d/%m/%Y %H.%M.%S'))
        
        return df

    def save_liquidity_movements(self, data: list[TransactionDTO], spreadsheet_id: str, sheet_name: str, cell: str) -> GoogleSheetStorageResponse:
        try:
            range = f"{sheet_name}!{cell}"
            
            existing_digests = self.load_ids(spreadsheet_id=spreadsheet_id, sheet=sheet_name, cell=cell)
            data = [t for t in data if t.digest not in existing_digests]

            if not data:
                return GoogleSheetStorageResponse(status="success", items_saved=0)
            
            df = self.convert_liquidity_movements(data=data)
            body = {
                'values': df.values.tolist()
            }

            self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            return GoogleSheetStorageResponse(status="success", items_saved=len(data))
        except Exception as e:
            return GoogleSheetStorageResponse(status="error", items_saved=0, error_message=str(e))

    def convert_portfolio_snapshot(self, data: list[PortfolioSnapshotDTO]) -> pd.DataFrame:
        df = pd.DataFrame([d.model_dump() for d in data])
        df['upload_date'] = df['upload_date'].apply(lambda x: x.strftime('%d/%m/%Y'))
        return df

    def save_portfolio_snapshot(self, data: list[PortfolioSnapshotDTO], spreadsheet_id: str, sheet_name: str, cell: str) -> GoogleSheetStorageResponse:
        
        try:
            range = f"{sheet_name}!{cell}"

            df = self.convert_portfolio_snapshot(data=data)
            self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body={
                    'values': df.values.tolist()
                }
            ).execute()
            return GoogleSheetStorageResponse(status="success", items_saved=len(df))            
        except Exception as e:
            return GoogleSheetStorageResponse(status="error", items_saved=0, error_message=str(e))
        
    def convert_portfolio_movements(self, data: list[PortfolioMovementDTO]) -> pd.DataFrame:
        
        COLUMNS = ['uid', 'digest', 'upload_datetime', 'value_date', 'accounting_date', 'title', 'isin', 'movement_type', 'unit_price', 'quantity', 'exchange_rate', 'invested_capital']
        df = pd.DataFrame([d.model_dump() for d in data])[COLUMNS]
        df['value_date'] = df['value_date'].apply(lambda x: x.strftime('%d/%m/%Y'))
        df['accounting_date'] = df['accounting_date'].apply(lambda x: x.strftime('%d/%m/%Y'))
        df['upload_datetime'] = df['upload_datetime'].apply(lambda x: x.strftime('%d/%m/%Y %H.%M.%S'))
        
        return df
    
    def save_portfolio_movements(self, data: list[PortfolioMovementDTO], spreadsheet_id: str, sheet_name: str, cell: str) -> GoogleSheetStorageResponse:
        range = f"{sheet_name}!{cell}"
        try:
            existing_digests = self.load_ids(spreadsheet_id=spreadsheet_id, sheet=sheet_name, cell=cell)
            data = [t for t in data if t.digest not in existing_digests]

            if not data:
                return GoogleSheetStorageResponse(status="success", items_saved=0)
        
            df = self.convert_portfolio_movements(data=data)
            body = {
                'values': df.values.tolist()
            }

            self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            return GoogleSheetStorageResponse(status="success", items_saved=len(data))
        except Exception as e:
            return GoogleSheetStorageResponse(status="error", items_saved=0, error_message=str(e))

    def load(self) -> list[TransactionDTO]:
        raise NotImplementedError("Load method is not implemented for GoogleSheetStorage.")