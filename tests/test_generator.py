import httpx
import pytest

from app.generator import RateLimitError, StreamingCodeGenerator


@pytest.fixture
def generator():
    api_key = "test-api-key"
    return StreamingCodeGenerator(api_key=api_key)


@pytest.mark.asyncio
async def test_generate_code_with_explanation_rate_limit(generator, mocker):
    # Mock the HTTP response from OpenAI API
    def mock_stream(*args, **kwargs):
        class MockResponse:
            status_code = 429
            headers = {"Retry-After": "2"}

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

            async def aiter_text(self):
                yield ""  # Yield an empty string to simulate no content

        return MockResponse()

    # Patch the httpx.AsyncClient.stream method
    mocker.patch("httpx.AsyncClient.stream", side_effect=mock_stream)

    # Call the method and expect RateLimitError
    with pytest.raises(RateLimitError):
        async for _ in generator.generate_code_with_explanation("Test prompt"):
            pass


@pytest.mark.asyncio
async def test_generate_code_with_explanation_timeout(generator, mocker):
    # Mock the HTTP client to raise a timeout exception
    def mock_stream(*args, **kwargs):
        class MockResponse:
            async def __aenter__(self):
                raise httpx.TimeoutException("Request timed out.")

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

        return MockResponse()

    # Patch the httpx.AsyncClient.stream method
    mocker.patch("httpx.AsyncClient.stream", side_effect=mock_stream)

    # Call the method and expect an exception
    with pytest.raises(Exception) as exc_info:
        async for _ in generator.generate_code_with_explanation("Test prompt"):
            pass

    assert "Request to OpenAI API timed out." in str(exc_info.value)
