from find_applicable_talent.util.logger import get_logger
from typing import Union
from cli_git_changelog.model_interface.model_interface import ModelInterface
from cli_git_changelog.model_interface import model_map, classify_model_name
import os
from dotenv import load_dotenv


load_dotenv()
logger = get_logger(__name__)


# MARK: this is a copy of the function in cli_git_changelog.model_interface.model_interface which is only a copy to clearly point to 
# where my actual code is coming from - I don't want to just duplicate it everywhere - check my other project for how I am both
# handling rate limiting and model selection and model interfacing 
def get_model(api_url: Union[str, None] = None, api_key: Union[str, None] = None, model: Union[str, None] = None) -> ModelInterface:
    """
    Get the model interface for the given model name. If the model name is not supported, raise an error.
    """
    api_url = api_url or os.getenv("API_URL")
    api_key = api_key or os.getenv("API_KEY")
    model = model or os.getenv("MODEL")
    logger.info(f"Using model: {model} api_url: {api_url} api_key is {'missing' if api_key is None else 'set'}")
    if api_key is None:
        logger.error("API_KEY is required")
        raise ValueError("API_KEY is required")

    if model is None:
        logger.error("Model is required")
        raise ValueError("Model is required")

    map_model_name = classify_model_name(model)
    if map_model_name in model_map:
        return model_map[map_model_name](api_url, api_key, model)
    logger.error(f"Unsupported model: {model}")
    raise ValueError(f"Unsupported model: {model}")
