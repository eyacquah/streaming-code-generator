import asyncio
import logging

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.config import API_KEY
from app.generator import MalformedResponseError, RateLimitError, StreamingCodeGenerator
from app.utils import async_call_with_retry_generator

router = APIRouter()
generator = StreamingCodeGenerator(api_key=API_KEY, request_timeout=30.0)

# Configure logging
logger = logging.getLogger(__name__)


class Prompt(BaseModel):
    prompt: str


@router.post("/generate-code/", status_code=status.HTTP_200_OK)
async def generate_code(payload: Prompt):
    """
    Endpoint to generate code with explanation using OpenAI's API.

    Args:
        payload (Prompt): The prompt data containing the user's prompt.

    Returns:
        StreamingResponse: An asynchronous streaming response with the generated code.
    """

    async def stream():
        try:
            async_gen = async_stream_generator(payload.prompt)
            async for content in async_gen:
                # Yield the content as plain text
                yield content
        except asyncio.TimeoutError:
            logger.error("Request handling timed out.")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="Request timed out."
            )
        except asyncio.CancelledError:
            logger.info("Client disconnected.")
            raise
        except Exception as e:
            logger.error(f"Error in stream: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    return StreamingResponse(stream(), media_type="text/plain")


async def async_stream_generator(prompt: str):
    """
    Asynchronous generator that streams data from the code generator with retries.

    Args:
        prompt (str): The user's prompt to send to the generator.

    Yields:
        str: The generated content chunk.
    """
    async for content in async_call_with_retry_generator(
        generator.generate_code_with_explanation,
        prompt,
        retries=3,
        delay=1,
        backoff=2,
        exceptions=(Exception, RateLimitError, MalformedResponseError),
        operation_timeout=60.0,  # Timeout per attempt
        total_timeout=120.0,  # Total timeout across all retries
    ):
        # Allow cancellation between chunks
        await asyncio.sleep(0)
        yield content
