from fastapi import FastAPI

from app.routes import router

app = FastAPI()
app.include_router(router)


app = FastAPI(
    title="Streaming Code Generator",
    description="API for real-time code generation and explanation",
    version="1.0.0",
)

# Include the router for endpoints
app.include_router(router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Streaming Code Generator API"}
