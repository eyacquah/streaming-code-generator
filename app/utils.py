import asyncio
import logging
import time

logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    pass


class MalformedResponseError(Exception):
    pass


async def async_call_with_retry_generator(
    func,
    *args,
    retries=3,
    delay=1,
    backoff=2,
    exceptions=(Exception,),
    operation_timeout=60.0,
    total_timeout=120.0,
    **kwargs,
):
    """
    Calls an asynchronous generator function with retry logic.

    Args:
        func (Callable): The asynchronous generator function to call.
        *args: Positional arguments to pass to the function.
        retries (int, optional): Number of retries. Defaults to 3.
        delay (float, optional): Initial delay between retries in seconds. Defaults to 1.
        backoff (int, optional): Backoff multiplier. Defaults to 2.
        exceptions (tuple, optional): Exceptions to catch and retry on. Defaults to (Exception,).
        operation_timeout (float, optional): Timeout per attempt. Defaults to 60.0.
        total_timeout (float, optional): Total timeout across all retries. Defaults to 120.0.
        **kwargs: Keyword arguments to pass to the function.

    Yields:
        Any: Items yielded by the generator function.
    """
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
                    item = await asyncio.wait_for(
                        gen.__anext__(), timeout=operation_timeout
                    )
                    yield item
                except StopAsyncIteration:
                    return
        except exceptions as e:
            current_time = time.monotonic()
            elapsed_time = current_time - start_time
            if elapsed_time >= total_timeout or attempt >= retries:
                logger.error(
                    f"Max retries or total timeout reached. Raising exception: {e}"
                )
                raise
            sleep_time = delay * (backoff ** (attempt - 1))
            logger.warning(
                f"Attempt {attempt} failed with {e!r}. Retrying in {sleep_time} seconds..."
            )
            await asyncio.sleep(sleep_time)
        else:
            break  # Exit the retry loop if successful
