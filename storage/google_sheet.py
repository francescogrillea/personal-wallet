import os

import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from model.transaction import TransactionDTO
from storage.base_storage import BaseStorage, BaseStorageResponse

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class GoogleSheetStorageResponse(BaseStorageResponse):
    ...

class GoogleSheetStorage(BaseStorage):

    def __init__(self, spreadsheet_id: str, range_name: str, *args, **kwargs):
        _credentials = self._load_credentials_from_env()
        _auth = service_account.Credentials.from_service_account_info(_credentials, scopes=SCOPES)

        self._spreadsheet_id = spreadsheet_id
        self._range_name = range_name

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

    def save(self, data: list[TransactionDTO]) -> GoogleSheetStorageResponse:
        try:
            df = pd.DataFrame([transaction.model_dump() for transaction in data])
            df['value_date'] = df['value_date'].apply(lambda x: x.strftime('%d/%m/%Y'))
            df['accounting_date'] = df['accounting_date'].apply(lambda x: x.strftime('%d/%m/%Y'))
            df['upload_datetime'] = df['upload_datetime'].apply(lambda x: x.strftime('%d/%m/%Y %H.%M.%S'))

            body = {
                'values': df.values.tolist()
            }

            self.service.spreadsheets().values().append(
                spreadsheetId=self._spreadsheet_id,
                range=self._range_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            return GoogleSheetStorageResponse(status="success", items_saved=len(data))
        except Exception as e:
            return GoogleSheetStorageResponse(status="error", items_saved=0, error_message=str(e))

    def load(self) -> list[TransactionDTO]:
        raise NotImplementedError("Load method is not implemented for GoogleSheetStorage.")