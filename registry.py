from parser.base_parser import ParserProviders
from parser.fineco import FinecoParser
from storage.google_sheet import GoogleSheetStorage
from storage.base_storage import StorageProviders

from config import AppConfig, get_object_from_config


class Registry:

    def __init__(self):

        self.config = get_object_from_config(config_model=AppConfig)
        self._init_registries()

        # set providers
        self.parsing_service = self.parsing_service_registry.get(self.config.parsing_service.provider)(
            **self.config.parsing_service.config)

        self.storage_service = self.storage_service_registry.get(self.config.storage_service.provider)(
            **self.config.storage_service.config)

    def _init_registries(self):
        """Initialize service registries mapping providers to their implementations."""
        self.parsing_service_registry = {
            ParserProviders.FINECO: FinecoParser
        }
        
        self.storage_service_registry = {
            StorageProviders.GOOGLE_SHEETS: GoogleSheetStorage
        }


registry = Registry()
