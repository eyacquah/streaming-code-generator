import pytest

from app.utils import async_call_with_retry_generator


@pytest.mark.asyncio
async def test_async_call_with_retry_generator_success():
    async def sample_generator():
        yield "chunk1"
        yield "chunk2"

    result = []
    async for item in async_call_with_retry_generator(sample_generator):
        result.append(item)

    assert result == ["chunk1", "chunk2"]
