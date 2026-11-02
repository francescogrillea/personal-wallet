from parser.fineco import FinecoParser
from storage.google_sheet import GoogleSheetStorage

from config import AppConfig, get_object_from_config


class Registry:

    def __init__(self):
        self.config = get_object_from_config(config_model=AppConfig)
        self.parser = FinecoParser
        self.storage = GoogleSheetStorage(**self.config.storage_service.model_dump())

registry = Registry()
