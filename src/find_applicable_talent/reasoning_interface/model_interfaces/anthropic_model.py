import requests
import time
import asyncio
from typing import List, Callable, Optional, Union, Tuple, Any
from anthropic import Anthropic, RateLimitError
from find_applicable_talent.reasoning_interface.model_interfaces.model_interface import ModelInterface
from find_applicable_talent.util.logger import get_logger
from find_applicable_talent.reasoning_interface.async_rate_limited_dispatcher import AsyncRateLimitedTaskDispatcher
from threading import Lock
from concurrent.futures import Future


logger = get_logger(__name__)


class AnthropicAPIReliantDispatcher:
    _instance = None
    _lock = Lock()
    CALLS = 50
    PERIOD = 60
    REFILL_INTERVAL = PERIOD / CALLS

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None: 
                    instance = super().__new__(cls)
                    instance.dispatcher = AsyncRateLimitedTaskDispatcher(
                        capacity=cls.CALLS,
                        refill_interval=cls.REFILL_INTERVAL
                    )
                    cls._instance = instance
                    logger.info(f"Anthropic API dispatcher initialized with {cls.CALLS} calls per {cls.PERIOD} seconds.")
                    logger.warn("This is a singleton. If this is logged more than once, something is wrong.")
        return cls._instance

    async def submit(self, method: Callable[..., Any], *args, **kwargs) -> Any:
        return await self.dispatcher.submit(method, *args, **kwargs)

class AnthropicModel(ModelInterface):
    MAX_RETRIES = 5

    def __init__(self, api_url: Union[str, None] = None, api_key: Union[str, None] = None, model: Union[str, None] = None) -> None:
        if api_url is not None and len(api_url) > 0:
            logger.warn(f"Anthropic API is auto interfered, overriding api_url: {api_url}")
            self.api_url = api_url
        else:
            self.api_url = "https://api.anthropic.com/v1/messages"
        if api_key is None:
            raise ValueError("API Key is required")
        self.api_key = api_key
        if model is None:
            self.model = "claude-3-5-sonnet-latest"
        else:
            self.model = model
        self.client = Anthropic(api_key=self.api_key)
        self.dispatcher = AnthropicAPIReliantDispatcher()


    def _normalize_inputs(self, prompt: str, temperature: float = 0.5, max_tokens: int = 4096) -> Tuple[str, float, int]:
        if prompt is None or len(prompt) == 0:
            raise ValueError("Prompt is required")
        if max_tokens is None or max_tokens == 0:
            max_tokens = 4096
        return prompt, temperature or 0.5, max_tokens


    async def submit_request(self, prompt: str, temperature: float = 0.5, max_tokens: int = 4096, method: Optional[Callable] = None) -> str:
        if method is None:
            method = self.query_model
        logger.info(f"Submitting request with prompt: {prompt[:25]}...")
        result = await self.dispatcher.submit(method, prompt, temperature, max_tokens)
        logger.info(f"Request completed with prompt: {prompt[:25]}...")
        return result


    async def call_model(self, prompt: str, temperature: float = 0.5, max_tokens: int = 4096) -> str:
        prompt, temperature, max_tokens = self._normalize_inputs(prompt, temperature, max_tokens)
        base_wait = 20  # seconds
        for attempt in range(self.MAX_RETRIES-1):
            try:
                return await self.submit_request(prompt, temperature, max_tokens)
            except RateLimitError:
                wait_time = base_wait * (attempt + 1)
                logger.warn(f"Rate limit hit (attempt {attempt + 1}/{self.MAX_RETRIES}). Sleeping for {wait_time}s...")
                await asyncio.sleep(wait_time)
            except Exception as e:
                err_msg = str(e).lower()
                if "rate" in err_msg and "limit" in err_msg:
                    wait_time = base_wait * (attempt + 1)
                    logger.warn(f"Rate limit-like error: {e} (attempt {attempt + 1}/{self.MAX_RETRIES}). Sleeping for {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    raise
        try:
            logger.warn("Falling back to raw HTTP request.")
            return await self.submit_request(prompt, temperature, max_tokens, self.query_model_requests)
        except Exception as e:
            logger.error(f"Anthropic request failed: {e}")
            raise


    def query_model_requests(self, prompt: str, temperature: float = 0.5, max_tokens: int = 4096) -> str:
        try:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }

            body = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature,
            }

            try:
                resp = requests.post(self.api_url, headers=headers, json=body, timeout=30)
                resp.raise_for_status()
            except requests.exceptions.RequestException as e:
                logger.error(f"Anthropic fallback HTTP request failed: {e}")
                raise RuntimeError(f"Anthropic fallback HTTP request failed: {e}")

            data = resp.json()
            if "content" in data and isinstance(data["content"], List):
                return "".join(block.get("text", "") for block in data["content"]).strip()

            logger.error(f"Unexpected API response: {data}")
            raise RuntimeError(f"Unexpected API response: {data}")
        except Exception as e:
            logger.error(f"Anthropic fallback HTTP request failed: {e}")
            raise


    def query_model(self, prompt: str, temperature: float = 0.5, max_tokens: int = 4096) -> str:
        try:
            response = self.client.messages.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            res = "".join(block.text for block in response.content if hasattr(block, "text")).strip()
            if not res:
                raise Exception(f"Anthropic returned empty response.")
            return res
        
        except RateLimitError as e:
            logger.warn(f"Anthropic rate limit hit: {e}")
            raise
        
        except Exception as e:
            logger.error(f"Anthropic request failed: {e}")
            raise
            