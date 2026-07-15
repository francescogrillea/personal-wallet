from pydantic import BaseModel
import os
import yaml

class ServiceConfig(BaseModel):
    provider: str
    config: dict

class AppConfig(BaseModel):
    storage_service: ServiceConfig

def get_object_from_config(config_model: type[AppConfig], filename: str = "config.yaml", abs_path: bool = False) -> AppConfig:
    """
    Loads a YAML configuration file from the specified path and returns it as a Pydantic object.

    Args:
        filename (str): The name of the configuration file.
        config_model (Type[Config]): The Pydantic model to validate the configuration against.
        abs_path: If True, the filename is treated as an absolute path. Defaults to False.

    Returns:
        Config: An instance of the Pydantic model populated with the configuration data.
    """
    if not abs_path:
        filepath = os.path.join(os.getenv("CONFIG_DIR", "config"), filename)
    else:
        filepath = filename

    with open(filepath, 'r') as file:
        config_dict = yaml.safe_load(file)
        result = config_model(**config_dict)

    return result
