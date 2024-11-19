import asyncio

import httpx

API_BASE_URL = "http://127.0.0.1:8000"  # Change if hosted elsewhere
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
                    error_message = await response.aread()  # Read error from stream
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
        try:
            # Sending an invalid payload to trigger an error
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


if __name__ == "__main__":
    # Ask the user for input dynamically
    test_prompt = input(
        "Enter your prompt (or press Enter to use the default): "
    ).strip()
    if not test_prompt:
        test_prompt = DEFAULT_PROMPT
        print(f"Using default prompt: {DEFAULT_PROMPT}")

    print("\nSelect a test to run:")
    print("1. Test generate code (normal)")
    print("2. Test generate code with timeout")
    print("3. Test generate code with invalid payload")

    test_choice = input("Enter the number of the test to run (default is 1): ").strip()
    if not test_choice:
        test_choice = "1"

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
                timeout_input = "0.1"
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
