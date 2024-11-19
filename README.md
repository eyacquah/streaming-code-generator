Streaming Code Generator

An API for real-time code generation and explanation using OpenAI’s GPT-4 model. This project allows users to send prompts to generate code along with explanations, streaming the responses in real-time.

Table of Contents

    •	Features
    •	Installation
    •	Configuration
    •	Usage
    •	Running the Application
    •	Using the API Client
    •	API Endpoints
    •	Testing
    •	Project Structure
    •	Contributing
    •	License
    •	Acknowledgements
    •	Contact

Features

    •	Real-time Streaming: Stream code generation and explanations in real-time using FastAPI and asynchronous generators.
    •	Retry Mechanism: Implements a retry mechanism with exponential backoff for handling transient errors and rate limits.
    •	Timeout Handling: Supports operation timeouts and total timeouts to ensure responsiveness.
    •	Asynchronous Design: Utilizes asynchronous programming for efficient I/O operations.
    •	Error Handling: Comprehensive error handling for various scenarios including timeouts, malformed responses, and rate limits.
    •	Testing: Includes tests for endpoints and utility functions.
    •	API Client: Provides an api_client.py script to interact with the API easily.

Installation

Prerequisites

    •	Python 3.7 or higher
    •	OpenAI API Key
    •	(Optional) Redis server for rate limiting (if implemented)

Steps

    1.	Clone the Repository

git clone https://github.com/yourusername/streaming-code-generator.git
cd streaming-code-generator

    2.	Create a Virtual Environment

python3 -m venv venv
source venv/bin/activate # On Windows, use `venv\Scripts\activate`

    3.	Install Dependencies

pip install --upgrade pip
pip install -r requirements.txt

Configuration

    1.	Set OpenAI API Key

Create a .env file in the root directory and add your OpenAI API key:

OPENAI_API_KEY=your_openai_api_key

    2.	Update Configuration (if necessary)

The app/config.py file reads environment variables. Ensure any other configurations are set appropriately.

Usage

Running the Application

    1.	Start the Server

uvicorn app.main:app --reload

This will start the server at http://127.0.0.1:8000.

    2.	Access the API
    •	Navigate to http://127.0.0.1:8000 to see the welcome message.
    •	API documentation is available at http://127.0.0.1:8000/docs.

Using the API Client

An api_client.py script is provided to interact with the API easily. This script allows you to test different scenarios and see how the API responds.

Steps to Use api_client.py

    1.	Ensure the Server is Running

Make sure you have the API server running as described in the Running the Application section. 2. Run the API Client Script

python api_client.py

    3.	Enter a Prompt

When prompted, enter the code prompt you want to send to the API. Press Enter to use the default prompt.

Enter your prompt (or press Enter to use the default):

    4.	Select a Test to Run

The script provides several test options:

Select a test to run:

1.  Test generate code (normal)
2.  Test generate code with timeout
3.  Test generate code with invalid payload
    Enter the number of the test to run (default is 1):

        •	Option 1: Sends a valid prompt and streams the response.
        •	Option 2: Tests how the API handles timeouts.
        •	You will be prompted to enter a timeout duration.
        •	Option 3: Sends an invalid payload to test error handling.

        5.	View the Output

    The script will display the API’s response or any error messages directly in the console.

Examples

    •	Example 1: Normal Test

python api_client.py

Enter your prompt (or press Enter to use the default):
Using default prompt: Create a function that sorts a list using bubble sort.

Select a test to run:

1.  Test generate code (normal)
2.  Test generate code with timeout
3.  Test generate code with invalid payload
    Enter the number of the test to run (default is 1):

        •	The script will stream and display the generated code and explanations.

        •	Example 2: Test with Timeout

python api_client.py

Enter your prompt (or press Enter to use the default): Implement a quicksort algorithm.

Select a test to run:

1.  Test generate code (normal)
2.  Test generate code with timeout
3.  Test generate code with invalid payload
    Enter the number of the test to run (default is 1): 2
    Enter timeout in seconds (default is 0.1):

        •	If the API takes longer than the specified timeout, the script will display a timeout error.

        •	Example 3: Test with Invalid Payload

python api_client.py

Enter your prompt (or press Enter to use the default): Any prompt.

Select a test to run:

1.  Test generate code (normal)
2.  Test generate code with timeout
3.  Test generate code with invalid payload
    Enter the number of the test to run (default is 1): 3

        •	The script sends an invalid payload to the API, and you can observe how the API handles bad requests.

API Endpoints

POST /generate-code/

    •	Description: Generates code with explanations based on the provided prompt. Streams the response in real-time.
    •	Request Body:

{
"prompt": "Your prompt here"
}

    •	Responses:
    •	200 OK: Stream of generated code and explanations.
    •	400 Bad Request: Invalid request payload.
    •	504 Gateway Timeout: Request timed out.
    •	500 Internal Server Error: An error occurred on the server.

Testing

Tests are written using pytest. To run the tests: 1. Install Test Dependencies
Ensure the following packages are installed:

pip install pytest pytest-asyncio httpx

    2.	Run Tests

pytest

This will execute all tests in the tests directory.

Project Structure

streaming-code-generator/
├── app/
│ ├── **init**.py
│ ├── main.py
│ ├── routes.py
│ ├── generator.py
│ ├── utils.py
│ └── config.py
├── tests/
│ ├── **init**.py
│ ├── test_routes.py
│ ├── test_generator.py
│ └── test_utils.py
├── api_client.py
├── requirements.txt
├── .pre-commit-config.yaml
├── .gitignore
└── README.md

    •	app/: Contains the main application modules.
    •	main.py: Entry point of the application.
    •	routes.py: Defines API endpoints and their handlers.
    •	generator.py: Logic for interacting with the OpenAI API.
    •	utils.py: Utility functions including retry logic.
    •	config.py: Configuration settings.
    •	tests/: Contains test cases for the application.
    •	api_client.py: Client script to test API endpoints.
    •	.pre-commit-config.yaml: Configuration for pre-commit hooks.
    •	requirements.txt: List of dependencies.
    •	README.md: Project documentation.

Code Overview

app/main.py

from fastapi import FastAPI
from app.routes import router

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

app/routes.py

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import logging

from app.config import API_KEY
from app.generator import StreamingCodeGenerator, RateLimitError, MalformedResponseError
from app.utils import async_call_with_retry_generator

router = APIRouter()
generator = StreamingCodeGenerator(api_key=API_KEY, request_timeout=30.0)

# Configure logging

logger = logging.getLogger(**name**)

class Prompt(BaseModel):
prompt: str

@router.post("/generate-code/", status_code=status.HTTP_200_OK)
async def generate_code(payload: Prompt):
async def stream():
try:
async_gen = async_stream_generator(payload.prompt)
async for content in async_gen:
yield content
except asyncio.TimeoutError:
logger.error("Request handling timed out.")
raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="Request timed out.")
except asyncio.CancelledError:
logger.info("Client disconnected.")
raise
except Exception as e:
logger.error(f"Error in stream: {e}")
raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")

    return StreamingResponse(stream(), media_type="text/plain")

async def async_stream_generator(prompt: str):
async for content in async_call_with_retry_generator(
generator.generate_code_with_explanation,
prompt,
retries=3,
delay=1,
backoff=2,
exceptions=(Exception, RateLimitError, MalformedResponseError),
operation_timeout=60.0,
total_timeout=120.0
):
await asyncio.sleep(0)
yield content

app/utils.py

import asyncio
import time
import logging

logger = logging.getLogger(**name**)

async def async_call_with_retry_generator(
func, \*args, retries=3, delay=1, backoff=2, exceptions=(Exception,), operation_timeout=60.0, total_timeout=120.0, \*\*kwargs
):
attempt = 0
start_time = time.monotonic()

    while True:
        attempt += 1
        try:
            gen = func(*args, **kwargs)
            while True:
                current_time = time.monotonic()
                elapsed_time = current_time - start_time
                if elapsed_time >= total_timeout:
                    raise asyncio.TimeoutError("Total timeout exceeded.")

                try:
                    item = await asyncio.wait_for(gen.__anext__(), timeout=operation_timeout)
                    yield item
                except StopAsyncIteration:
                    return
        except exceptions as e:
            current_time = time.monotonic()
            elapsed_time = current_time - start_time
            if elapsed_time >= total_timeout or attempt >= retries:
                logger.error(f"Max retries or total timeout reached. Raising exception: {e}")
                raise
            sleep_time = delay * (backoff ** (attempt - 1))
            logger.warning(f"Attempt {attempt} failed with {e!r}. Retrying in {sleep_time} seconds...")
            await asyncio.sleep(sleep_time)
        else:
            break

api_client.py

import asyncio
import httpx

API_BASE_URL = "http://127.0.0.1:8000" # Change if hosted elsewhere
DEFAULT_PROMPT = "Create a function that sorts a list using bubble sort."

async def test_generate_code(prompt: str):
"""
Test the `/generate-code/` endpoint by sending a prompt and printing the streamed response.
"""
print("\nRunning Test: Generate Code (Normal)")
async with httpx.AsyncClient() as client:
try:
async with client.stream(
"POST", f"{API_BASE_URL}/generate-code/", json={"prompt": prompt}
) as response:
if response.status_code != 200:
error_message = await response.aread() # Read error from stream
print(
f"Error: {response.status_code} - {error_message.decode('utf-8')}"
)
return

                print("\nStreaming response:")
                async for chunk in response.aiter_text():
                    print(chunk, end="")
        except httpx.RequestError as e:
            print(f"An error occurred while requesting the API: {e}")

async def test_generate_code_timeout(prompt: str, timeout: float):
"""
Test the `/generate-code/` endpoint with a timeout to simulate a slow response.
"""
print("\nRunning Test: Generate Code with Timeout")
async with httpx.AsyncClient(timeout=timeout) as client:
try:
async with client.stream(
"POST", f"{API_BASE_URL}/generate-code/", json={"prompt": prompt}
) as response:
if response.status_code != 200:
error_message = await response.aread()
print(
f"Error: {response.status_code} - {error_message.decode('utf-8')}"
)
return

                print("\nStreaming response:")
                async for chunk in response.aiter_text():
                    print(chunk, end="")
        except httpx.ReadTimeout:
            print(f"Request timed out after {timeout} seconds.")
        except httpx.RequestError as e:
            print(f"An error occurred while requesting the API: {e}")

async def test_generate_code_invalid_payload(prompt: str):
"""
Test the `/generate-code/` endpoint with an invalid payload to trigger a 400 error.
"""
print("\nRunning Test: Generate Code with Invalid Payload")
async with httpx.AsyncClient() as client:
try: # Sending an invalid payload to trigger an error
async with client.stream(
"POST", f"{API_BASE_URL}/generate-code/", json={"invalid_key": prompt}
) as response:
if response.status_code != 200:
error_message = await response.aread()
print(
f"Error: {response.status_code} - {error_message.decode('utf-8')}"
)
return

                print("\nStreaming response:")
                async for chunk in response.aiter_text():
                    print(chunk, end="")
        except httpx.RequestError as e:
            print(f"An error occurred while requesting the API: {e}")

if **name** == "**main**": # Ask the user for input dynamically
test_prompt = input("Enter your prompt (or press Enter to use the default): ").strip()
if not test_prompt:
test_prompt = DEFAULT_PROMPT
print(f"Using default prompt: {DEFAULT_PROMPT}")

    print("\nSelect a test to run:")
    print("1. Test generate code (normal)")
    print("2. Test generate code with timeout")
    print("3. Test generate code with invalid payload")

    test_choice = input("Enter the number of the test to run (default is 1): ").strip()
    if not test_choice:
        test_choice = '1'

    try:
        test_choice = int(test_choice)
    except ValueError:
        print("Invalid choice. Defaulting to test 1.")
        test_choice = 1

    if test_choice == 1:
        asyncio.run(test_generate_code(test_prompt))
    elif test_choice == 2:
        try:
            timeout_input = input("Enter timeout in seconds (default is 0.1): ").strip()
            if not timeout_input:
                timeout_input = '0.1'
            timeout = float(timeout_input)
        except ValueError:
            print("Invalid timeout. Defaulting to 0.1 seconds.")
            timeout = 0.1
        asyncio.run(test_generate_code_timeout(test_prompt, timeout))
    elif test_choice == 3:
        asyncio.run(test_generate_code_invalid_payload(test_prompt))
    else:
        print("Invalid choice. Running test 1 by default.")
        asyncio.run(test_generate_code(test_prompt))

Contributing

Contributions are welcome! Please follow these steps: 1. Fork the Repository 2. Create a Feature Branch

git checkout -b feature/your-feature-name

    3.	Make Changes and Commit

Ensure code formatting and tests pass before committing.

pre-commit run --all-files
git add .
git commit -m "Your descriptive commit message"

    4.	Push to Your Fork and Create a Pull Request

Pre-commit Hooks

This project uses pre-commit hooks to maintain code quality.

Configuration (.pre-commit-config.yaml):

repos:

- repo: https://github.com/psf/black
  rev: 24.10.0
  hooks:

  - id: black

- repo: https://github.com/PyCQA/isort
  rev: 5.13.2
  hooks:

  - id: isort

- repo: https://github.com/pycqa/flake8
  rev: 6.1.0
  hooks:

  - id: flake8

- repo: local
  hooks:
  - id: pytest
    name: Run tests with pytest
    entry: pytest
    language: system
    types: [python]
    pass_filenames: false

Install Pre-commit Hooks:

pip install pre-commit
pre-commit install

Now, tests and linters will run automatically before each commit.

License

This project is licensed under the MIT License. See the LICENSE file for details.

Acknowledgements

    •	OpenAI for providing the GPT-4 model.
    •	FastAPI for the web framework.
    •	httpx for asynchronous HTTP requests.
    •	tiktoken for token encoding.

Contact

    •	Author: Emmanuel Yaw Acquah
    •	Email: eyacquah0@gmail.com
    •	GitHub: eyacquah

Feel free to reach out for any questions or suggestions!
