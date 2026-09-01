import os
from itertools import chain

import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from model.transaction import TransactionDTO
from model.portfolio import PortfolioSnapshotDTO
from storage.base_storage import BaseStorage, BaseStorageResponse

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class GoogleSheetStorageResponse(BaseStorageResponse):
    ...

class GoogleSheetStorage(BaseStorage):

    # def __init__(self, spreadsheet_id: str, range_name: str, *args, **kwargs):
    def __init__(self, *args, **kwargs):
        _credentials = self._load_credentials_from_env()
        _auth = service_account.Credentials.from_service_account_info(_credentials, scopes=SCOPES)

        # self._spreadsheet_id = spreadsheet_id
        # self._range_name = range_name

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

    def save_transactions(self, data: list[TransactionDTO], **kwargs) -> GoogleSheetStorageResponse:
        try:
            spreadsheet_id: str = kwargs['spreadsheet_id']
            sheet_name: str = kwargs['sheet_name']
            cell: str = kwargs['cell']
            range = f"{sheet_name}!{cell}"
            
            existing_digests = self.load_ids(spreadsheet_id=spreadsheet_id, sheet=sheet_name, cell=cell)
            data = [t for t in data if t.digest not in existing_digests]

            if not data:
                return GoogleSheetStorageResponse(status="success", items_saved=0)

            COLUMNS = ['uid', 'digest', 'upload_datetime', 'value_date', 'accounting_date', 'amount', 'description', 'category']
            df = pd.DataFrame([transaction.model_dump() for transaction in data])[COLUMNS]
            df['value_date'] = df['value_date'].apply(lambda x: x.strftime('%d/%m/%Y'))
            df['accounting_date'] = df['accounting_date'].apply(lambda x: x.strftime('%d/%m/%Y'))
            df['upload_datetime'] = df['upload_datetime'].apply(lambda x: x.strftime('%d/%m/%Y %H.%M.%S'))

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

    def save_portfolio(self, data: list[PortfolioSnapshotDTO], **kwargs) -> GoogleSheetStorageResponse:
        
        try:
            spreadsheet_id: str = kwargs['spreadsheet_id']
            sheet_name: str = kwargs['sheet_name']
            cell: str = kwargs['cell']
            range = f"{sheet_name}!{cell}"
            
            df = pd.DataFrame([d.model_dump() for d in data])
            df['upload_date'] = df['upload_date'].apply(lambda x: x.strftime('%d/%m/%Y'))

            
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
        
        

    def load(self) -> list[TransactionDTO]:
        raise NotImplementedError("Load method is not implemented for GoogleSheetStorage.")