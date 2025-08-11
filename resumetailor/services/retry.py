"""
Retry utility with exponential backoff for handling rate limits and other transient errors.
"""
import time
import logging
import random
import os
from typing import Callable, Any, Type, Union
from functools import wraps
from openai import RateLimitError, APIError, APIConnectionError
from langchain_core.exceptions import LangChainException

logger = logging.getLogger(__name__)

# Default retry configuration (can be overridden by environment variables)
DEFAULT_MAX_RETRIES = int(os.getenv("RETRY_MAX_RETRIES", "5"))
DEFAULT_BASE_DELAY = float(os.getenv("RETRY_BASE_DELAY", "1.0"))
DEFAULT_MAX_DELAY = float(os.getenv("RETRY_MAX_DELAY", "300.0"))  # 5 minutes
DEFAULT_BACKOFF_FACTOR = float(os.getenv("RETRY_BACKOFF_FACTOR", "2.0"))
DEFAULT_JITTER = os.getenv("RETRY_JITTER", "true").lower() in ("true", "1", "yes")

# Retryable exceptions
RETRYABLE_EXCEPTIONS = (
    RateLimitError,
    APIConnectionError,
    APIError,
    LangChainException,
)


def extract_retry_after(error: Exception) -> float | None:
    """
    Extract retry-after value from error message or headers.
    
    Args:
        error: The exception that was raised
        
    Returns:
        float | None: Number of seconds to wait, or None if not found
    """
    if isinstance(error, RateLimitError):
        # OpenAI rate limit errors often include retry-after information
        error_message = str(error)
        if "try again in" in error_message.lower():
            try:
                # Extract time from messages like "Please try again in 3.234s"
                import re
                match = re.search(r'try again in (\d+\.?\d*)s', error_message)
                if match:
                    return float(match.group(1))
            except (ValueError, AttributeError):
                pass
    return None


def exponential_backoff_with_jitter(
    attempt: int,
    base_delay: float = DEFAULT_BASE_DELAY,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    max_delay: float = DEFAULT_MAX_DELAY,
    jitter: bool = DEFAULT_JITTER,
) -> float:
    """
    Calculate exponential backoff delay with optional jitter.
    
    Args:
        attempt: Current attempt number (0-indexed)
        base_delay: Base delay in seconds
        backoff_factor: Multiplier for exponential backoff
        max_delay: Maximum delay in seconds
        jitter: Whether to add random jitter
        
    Returns:
        float: Delay in seconds
    """
    delay = base_delay * (backoff_factor ** attempt)
    delay = min(delay, max_delay)
    
    if jitter:
        # Add random jitter of ±25%
        jitter_range = delay * 0.25
        delay += random.uniform(-jitter_range, jitter_range)
    
    return max(0, delay)


def retry_with_exponential_backoff(
    max_retries: int = DEFAULT_MAX_RETRIES,
    base_delay: float = DEFAULT_BASE_DELAY,
    max_delay: float = DEFAULT_MAX_DELAY,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    jitter: bool = DEFAULT_JITTER,
    retryable_exceptions: tuple[Type[Exception], ...] = RETRYABLE_EXCEPTIONS,
    respect_retry_after: bool = True,
):
    """
    Decorator to retry function calls with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds for exponential backoff
        max_delay: Maximum delay in seconds
        backoff_factor: Multiplier for exponential backoff
        jitter: Whether to add random jitter to delays
        retryable_exceptions: Tuple of exception types that should trigger retries
        respect_retry_after: Whether to respect retry-after hints from errors
        
    Returns:
        Decorated function that will retry on failure
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        func_name = getattr(func, '__name__', 'unknown_function')
                        logger.error(
                            f"Function {func_name} failed after {max_retries + 1} attempts. "
                            f"Last error: {e}"
                        )
                        raise e
                    
                    # Calculate delay
                    if respect_retry_after:
                        retry_after = extract_retry_after(e)
                        if retry_after:
                            delay = retry_after + random.uniform(0.1, 0.5)  # Add small jitter to retry-after
                        else:
                            delay = exponential_backoff_with_jitter(
                                attempt, base_delay, backoff_factor, max_delay, jitter
                            )
                    else:
                        delay = exponential_backoff_with_jitter(
                            attempt, base_delay, backoff_factor, max_delay, jitter
                        )
                    
                    func_name = getattr(func, '__name__', 'unknown_function')
                    logger.warning(
                        f"Function {func_name} failed on attempt {attempt + 1}/{max_retries + 1}. "
                        f"Error: {e}. Retrying in {delay:.2f} seconds..."
                    )
                    
                    time.sleep(delay)
                except Exception as e:
                    # Non-retryable exception, fail immediately
                    func_name = getattr(func, '__name__', 'unknown_function')
                    logger.error(f"Function {func_name} failed with non-retryable error: {e}")
                    raise e
            
            # This should never be reached due to the raise in the loop
            raise last_exception
        
        return wrapper
    return decorator


class RetryableChain:
    """
    Wrapper class for LangChain chains that adds retry functionality.
    """
    
    def __init__(
        self,
        chain: Any,
        max_retries: int = DEFAULT_MAX_RETRIES,
        base_delay: float = DEFAULT_BASE_DELAY,
        max_delay: float = DEFAULT_MAX_DELAY,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
        jitter: bool = DEFAULT_JITTER,
    ):
        self.chain = chain
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
    
    @property
    def invoke(self):
        """Return a retryable version of the chain's invoke method."""
        return retry_with_exponential_backoff(
            max_retries=self.max_retries,
            base_delay=self.base_delay,
            max_delay=self.max_delay,
            backoff_factor=self.backoff_factor,
            jitter=self.jitter,
        )(self.chain.invoke)
    
    def __getattr__(self, name):
        """Delegate other attributes to the wrapped chain."""
        return getattr(self.chain, name)


# Convenience function for one-off retries
def retry_llm_call(
    func: Callable,
    *args,
    max_retries: int = DEFAULT_MAX_RETRIES,
    **kwargs
) -> Any:
    """
    Execute a function with retry logic.
    
    Args:
        func: Function to execute
        *args: Positional arguments for the function
        max_retries: Maximum number of retry attempts
        **kwargs: Keyword arguments for the function
        
    Returns:
        Result of the function call
    """
    @retry_with_exponential_backoff(max_retries=max_retries)
    def wrapper():
        return func(*args, **kwargs)
    
    return wrapper()