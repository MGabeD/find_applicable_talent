from typing import Union
from find_applicable_talent.reasoning_interface.model_interfaces.anthropic_model import AnthropicModel
from find_applicable_talent.reasoning_interface.model_interfaces.model_interface import ModelInterface
from find_applicable_talent.util.logger import get_logger
import os


logger = get_logger(__name__)


model_map = {
    "claude": AnthropicModel,
}


def classify_model_name(model: str) -> str:
    """
    Classify the model name to a standard format. For example: claude-3-5-xxxx -> claude (its the same interface)
    """
    model_name = model.lower()
    if "claude" in model_name:
        return "claude"
    return model_name


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
        raise ValueError("Model is required")
    map_model_name = classify_model_name(model)
    if map_model_name in model_map:
        return model_map[map_model_name](api_url, api_key, model)
    logger.error(f"Unsupported model: {model}")
    raise ValueError(f"Unsupported model: {model}")