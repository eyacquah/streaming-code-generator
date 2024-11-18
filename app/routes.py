from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.generator import StreamingCodeGenerator

router = APIRouter()

# Initialize the code generator (use your OpenAI API key here)
generator = StreamingCodeGenerator(api_key="your_openai_api_key")

@router.post("/generate-code/")
async def generate_code(prompt: str):
    async def stream():
        async for chunk in generator.generate_code_with_explanation(prompt, lambda x: x):
            yield chunk
    return StreamingResponse(stream(), media_type="text/plain")