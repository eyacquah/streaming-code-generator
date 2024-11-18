import asyncio
from typing import Callable, AsyncIterator
import httpx

class StreamingCodeGenerator:
    """
    A class to interact with the OpenAI API for generating and explaining code in real-time.

    This class handles the initialization, streaming requests to the OpenAI API,
    and processing the streamed chunks of response data.
    """

    def __init__(self, api_key: str):
        """
        Initialize the StreamingCodeGenerator with an API key and endpoint.

        Args:
            api_key (str): The API key for authenticating requests to OpenAI.
        """
        self.api_key = api_key
        self.api_url = "https://api.openai.com/v1/chat/completions"

    async def generate_code_with_explanation(
        self, prompt: str, callback: Callable[[str], None]
    ) -> AsyncIterator[str]:
        """
        Stream code generation and explanation from OpenAI API.

        Args:
            prompt (str): A description of the code to generate.
            callback (Callable[[str], None]): A callback function to process each chunk of the response.

        Yields:
            str: Formatted chunks of the response streamed from the OpenAI API.

        Raises:
            Exception: If the API returns a non-200 status code.
        """
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": prompt}],
            "stream": True
        }

        async with httpx.AsyncClient() as client:
            async with client.stream("POST", self.api_url, json=payload, headers=headers) as response:
                if response.status_code != 200:
                    raise Exception(f"API Error: {response.status_code} {response.text}")
                async for chunk in response.aiter_text():
                    formatted = self.format_chunk(chunk)
                    if callback:
                        callback(formatted)
                    yield formatted

    def format_chunk(self, chunk: str) -> str:
        """
        Format a raw chunk of the response for better readability.

        Args:
            chunk (str): The raw chunk of data from the API response.

        Returns:
            str: The formatted chunk of data.
        """
        # Placeholder for any specific formatting logic.
        return chunk