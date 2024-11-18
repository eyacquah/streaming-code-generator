from fastapi import FastAPI
from dotenv import load_dotenv
from app.routes import router
import os

# Load environment variables
load_dotenv()

# Get the API key
API_KEY = os.getenv("API_KEY")

app = FastAPI(
    title="Streaming Code Generator",
    description="API for real-time code generation and explanation",
    version="1.0.0"
)

# Include the router for endpoints
app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Streaming Code Generator API"}