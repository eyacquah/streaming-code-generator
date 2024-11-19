import asyncio
import json
import logging
from typing import AsyncGenerator, Callable, Optional

import httpx
import tiktoken  # For token counting

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    """Custom exception for rate limit errors."""

    pass


class MalformedResponseError(Exception):
    """Custom exception for malformed responses."""

    pass


class StreamingCodeGenerator:
    """
    A class to interact with the OpenAI API and stream code generation with explanations.
    Includes token tracking.
    """

    def __init__(
        self,
        api_key: str,
        request_timeout: float = 30.0,
        max_parse_errors: int = 5,
        model: str = "gpt-4",
    ):
        """
        Initialize the StreamingCodeGenerator.

        Args:
            api_key (str): OpenAI API key.
            request_timeout (float, optional): Timeout for the API request. Defaults to 30.0.
            max_parse_errors (int, optional): Maximum allowed consecutive parse errors before aborting. Defaults to 5.
            model (str, optional): Model to use for code generation. Defaults to "gpt-4".
        """
        self.api_key = api_key
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.request_timeout = request_timeout
        self.max_parse_errors = max_parse_errors
        self.model = model
        self.tokenizer = tiktoken.encoding_for_model(model)

    async def generate_code_with_explanation(
        self,
        prompt: str,
        callback: Optional[Callable[[str], None]] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream OpenAI API responses and yield chunks iteratively with token tracking.

        Args:
            prompt (str): The prompt to send to the OpenAI API.
            callback (Callable[[str], None], optional): A callback function to process each chunk.

        Yields:
            str: The generated content chunk.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an assistant that provides code with explanations.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.7,
            "stream": True,
        }

        malformed_response_count = 0  # Counter for consecutive parse errors
        total_tokens = 0  # Total tokens generated
        max_malformed_responses = self.max_parse_errors

        timeout = httpx.Timeout(self.request_timeout)

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                async with client.stream(
                    "POST", self.api_url, json=payload, headers=headers
                ) as response:

                    if response.status_code == 429:
                        retry_after = int(
                            response.headers.get("Retry-After", "5")
                        )  # Default to 5 seconds
                        logger.warning(
                            f"Rate limit exceeded. Retry after {retry_after} seconds."
                        )
                        raise RateLimitError("Rate limit exceeded.")

                    elif response.status_code != 200:
                        logger.error(
                            f"API Error: {response.status_code} {response.text}"
                        )
                        raise Exception(
                            f"API Error: {response.status_code} {response.text}"
                        )

                    async for line in response.aiter_lines():
                        if line.strip() == "":
                            continue
                        if line.startswith("data:"):
                            part = line.replace("data:", "").strip()
                            if part == "[DONE]":
                                break
                            try:
                                parsed = json.loads(part)
                                malformed_response_count = (
                                    0  # Reset counter on successful parse
                                )
                                delta = parsed["choices"][0]["delta"]
                                if "content" in delta:
                                    content = delta["content"]
                                    # Count tokens in the content
                                    tokens = len(self.tokenizer.encode(content))
                                    total_tokens += tokens

                                    if callback:
                                        callback(content)

                                    yield content
                            except json.JSONDecodeError as e:
                                malformed_response_count += 1
                                logger.error(f"Failed to parse part: {e}")
                                if malformed_response_count >= max_malformed_responses:
                                    logger.error(
                                        "Too many malformed responses. Aborting."
                                    )
                                    raise MalformedResponseError(
                                        "Too many malformed responses."
                                    )
                                continue  # Skip to the next part
            except asyncio.CancelledError:
                logger.info("Streaming cancelled by client.")
                raise  # Re-raise the exception to propagate cancellation
            except httpx.TimeoutException:
                logger.error("Request to OpenAI API timed out.")
                raise Exception("Request to OpenAI API timed out.")
            except RateLimitError:
                raise  # Re-raise to be caught by retry mechanism
            except Exception as e:
                logger.error(f"Error in generate_code_with_explanation: {e}")
                raise
