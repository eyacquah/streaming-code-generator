import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.routes import generator


@pytest.mark.asyncio
async def test_generate_code_success(mocker):
    # Mock the async generator to yield sample data
    async def mock_async_stream_generator(prompt):
        yield "Sample code"

    # Patch the generator's method
    mocker.patch.object(
        generator,
        "generate_code_with_explanation",
        return_value=mock_async_stream_generator(""),
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        response = await ac.post("/generate-code/", json={"prompt": "Test prompt"})

    assert response.status_code == status.HTTP_200_OK
    assert response.text == "Sample code"
