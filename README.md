# Streaming Code Generator

An API for real-time code generation and explanation using OpenAI’s GPT-4 model. This project allows users to send prompts to generate code along with explanations, streaming the responses in real-time.

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Steps](#steps)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Running the Application](#running-the-application)
  - [Using the API Client](#using-the-api-client)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [Pre-commit Hooks](#pre-commit-hooks)
- [License](#license)
- [Acknowledgements](#acknowledgements)
- [Contact](#contact)

---

## Features

- **Real-time Streaming**: Stream code generation and explanations in real-time using FastAPI and asynchronous generators.
- **Retry Mechanism**: Implements a retry mechanism with exponential backoff for handling transient errors and rate limits.
- **Timeout Handling**: Supports operation timeouts and total timeouts to ensure responsiveness.
- **Asynchronous Design**: Utilizes asynchronous programming for efficient I/O operations.
- **Error Handling**: Comprehensive error handling for various scenarios including timeouts, malformed responses, and rate limits.
- **Testing**: Includes tests for endpoints and utility functions.
- **API Client**: Provides an `api_client.py` script to interact with the API easily.

---

## Installation

### Prerequisites

- Python 3.7 or higher
- OpenAI API Key
- _(Optional)_ Redis server for rate limiting (if implemented)

### Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/streaming-code-generator.git
   cd streaming-code-generator

   2.	Create a Virtual Environment
   ```

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

Ensure any other configurations are set appropriately in the app/config.py file.

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

Ensure the API server is running as described in Running the Application. 2. Run the API Client Script

python api_client.py

    3.	Enter a Prompt

When prompted, enter the code prompt you want to send to the API. Press Enter to use the default prompt. 4. Select a Test to Run
The script provides several test options:
• Option 1: Sends a valid prompt and streams the response.
• Option 2: Tests how the API handles timeouts.
• Option 3: Sends an invalid payload to test error handling. 5. View the Output
The script will display the API’s response or any error messages directly in the console.

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

pip install pytest pytest-asyncio httpx

    2.	Run Tests

pytest

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

Configuration (.pre-commit-config.yaml)

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
    args: [--ignore=E501] # Ignore line length errors

- repo: local
  hooks:
  - id: pytest
    name: Run tests with pytest
    entry: pytest
    language: system
    types: [python]
    pass_filenames: false

Install Pre-commit Hooks

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
