"""
Tests for the retry mechanism with exponential backoff for rate limits and other transient errors.
"""
import pytest
import time
import re
from unittest.mock import Mock, patch, MagicMock
from openai import RateLimitError, APIConnectionError, APIError
from langchain_core.exceptions import LangChainException

from resumetailor.services.retry import (
    RetryableChain,
    retry_with_exponential_backoff,
    exponential_backoff_with_jitter,
    extract_retry_after,
    retry_llm_call,
    DEFAULT_MAX_RETRIES,
)


@pytest.fixture
def mock_rate_limit_error():
    """Create a mock OpenAI RateLimitError with retry-after information."""
    error_message = (
        "Error code: 429 - {'error': {'message': 'Rate limit reached for gpt-5 in organization "
        "org-LPbUyB8fsMaxoaMRE1F7Pb1Y on tokens per min (TPM): Limit 30000, Used 30000, "
        "Requested 1617. Please try again in 3.234s. Visit https://platform.openai.com/account/rate-limits⁠ "
        "to learn more.', 'type': 'tokens', 'param': None, 'code': 'rate_limit_exceeded'}}"
    )
    return RateLimitError(
        message=error_message,
        response=Mock(status_code=429),
        body={"error": {"code": "rate_limit_exceeded"}}
    )


@pytest.fixture
def mock_connection_error():
    """Create a mock APIConnectionError."""
    return APIConnectionError(request=Mock())


@pytest.fixture
def mock_api_error():
    """Create a mock APIError."""
    return APIError(message="API error occurred", request=Mock(), body={})


@pytest.fixture
def mock_langchain_error():
    """Create a mock LangChain error."""
    return LangChainException("LangChain error")


@pytest.fixture
def mock_failing_function():
    """Create a mock function that fails with rate limits before succeeding."""
    def create_failing_function(fail_count=2, success_result="success"):
        call_count = {"count": 0}
        
        def failing_function(*args, **kwargs):
            call_count["count"] += 1
            if call_count["count"] <= fail_count:
                error_message = f"Rate limit reached. Please try again in {1.5}s."
                raise RateLimitError(
                    message=error_message,
                    response=Mock(status_code=429),
                    body={"error": {"code": "rate_limit_exceeded"}}
                )
            return success_result
        
        failing_function.call_count = call_count
        return failing_function
    
    return create_failing_function


@pytest.fixture
def mock_chain():
    """Create a mock LangChain chain for testing."""
    chain = Mock()
    chain.invoke = Mock(return_value="chain result")
    return chain


class TestRetryUtilities:
    """Test utility functions for retry mechanism."""
    
    def test_extract_retry_after_from_rate_limit_error(self, mock_rate_limit_error):
        """Test extraction of retry-after time from OpenAI rate limit error."""
        retry_after = extract_retry_after(mock_rate_limit_error)
        assert retry_after == 3.234
    
    def test_extract_retry_after_from_generic_error(self, mock_connection_error):
        """Test extraction returns None for non-rate-limit errors."""
        retry_after = extract_retry_after(mock_connection_error)
        assert retry_after is None
    
    def test_exponential_backoff_calculation(self):
        """Test exponential backoff delay calculation."""
        # Test basic exponential backoff
        delay_0 = exponential_backoff_with_jitter(0, base_delay=1.0, backoff_factor=2.0, jitter=False)
        delay_1 = exponential_backoff_with_jitter(1, base_delay=1.0, backoff_factor=2.0, jitter=False)
        delay_2 = exponential_backoff_with_jitter(2, base_delay=1.0, backoff_factor=2.0, jitter=False)
        
        assert delay_0 == 1.0
        assert delay_1 == 2.0
        assert delay_2 == 4.0
    
    def test_exponential_backoff_max_delay(self):
        """Test that exponential backoff respects max_delay."""
        delay = exponential_backoff_with_jitter(10, base_delay=1.0, backoff_factor=2.0, max_delay=5.0, jitter=False)
        assert delay == 5.0
    
    def test_exponential_backoff_with_jitter(self):
        """Test that jitter adds randomness to delay."""
        delays = [
            exponential_backoff_with_jitter(1, base_delay=2.0, backoff_factor=2.0, jitter=True)
            for _ in range(10)
        ]
        
        # All delays should be around 4.0 ± 25%
        for delay in delays:
            assert 3.0 <= delay <= 5.0
        
        # Delays should not all be identical (due to jitter)
        assert len(set(delays)) > 1


class TestRetryDecorator:
    """Test the retry decorator functionality."""
    
    def test_successful_function_no_retries(self):
        """Test that successful functions work without retries."""
        @retry_with_exponential_backoff(max_retries=3)
        def successful_function(value):
            return f"success: {value}"
        
        result = successful_function("test")
        assert result == "success: test"
    
    @patch('time.sleep')  # Mock sleep to speed up test
    def test_function_succeeds_after_retries(self, mock_sleep, mock_failing_function):
        """Test that function succeeds after retrying on rate limits."""
        failing_func = mock_failing_function(fail_count=2)
        
        @retry_with_exponential_backoff(max_retries=5, base_delay=0.1)
        def decorated_function():
            return failing_func()
        
        result = decorated_function()
        assert result == "success"
        assert failing_func.call_count["count"] == 3  # Failed twice, succeeded on third
        assert mock_sleep.call_count == 2  # Slept twice
    
    @patch('time.sleep')
    def test_function_fails_after_max_retries(self, mock_sleep, mock_failing_function):
        """Test that function fails after exhausting max retries."""
        failing_func = mock_failing_function(fail_count=10)  # Always fail
        
        @retry_with_exponential_backoff(max_retries=2, base_delay=0.1)
        def decorated_function():
            return failing_func()
        
        with pytest.raises(RateLimitError):
            decorated_function()
        
        assert failing_func.call_count["count"] == 3  # Initial call + 2 retries
        assert mock_sleep.call_count == 2
    
    @patch('time.sleep')
    def test_respect_retry_after_header(self, mock_sleep, mock_rate_limit_error):
        """Test that retry respects the retry-after time from rate limit errors."""
        call_count = {"count": 0}
        
        def failing_function():
            call_count["count"] += 1
            if call_count["count"] == 1:
                raise mock_rate_limit_error
            return "success"
        
        @retry_with_exponential_backoff(max_retries=3, base_delay=1.0, respect_retry_after=True)
        def decorated_function():
            return failing_function()
        
        result = decorated_function()
        assert result == "success"
        
        # Check that sleep was called with approximately the retry-after time (3.234s + jitter)
        sleep_calls = mock_sleep.call_args_list
        assert len(sleep_calls) == 1
        sleep_time = sleep_calls[0][0][0]
        assert 3.2 <= sleep_time <= 4.0  # 3.234 + small jitter
    
    def test_non_retryable_exception_fails_immediately(self):
        """Test that non-retryable exceptions fail immediately without retries."""
        @retry_with_exponential_backoff(max_retries=3)
        def function_with_value_error():
            raise ValueError("This should not be retried")
        
        with pytest.raises(ValueError, match="This should not be retried"):
            function_with_value_error()
    
    @patch('time.sleep')
    def test_different_retryable_exceptions(self, mock_sleep):
        """Test that different retryable exception types are handled."""
        exceptions = [
            APIConnectionError(request=Mock()),
            APIError(message="API error", request=Mock(), body={}),
            LangChainException("LangChain error"),
        ]
        
        for exception in exceptions:
            call_count = {"count": 0}
            
            def failing_function():
                call_count["count"] += 1
                if call_count["count"] == 1:
                    raise exception
                return "success"
            
            @retry_with_exponential_backoff(max_retries=2, base_delay=0.1)
            def decorated_function():
                return failing_function()
            
            result = decorated_function()
            assert result == "success"
            assert call_count["count"] == 2


class TestRetryableChain:
    """Test the RetryableChain wrapper class."""
    
    def test_retryable_chain_success(self, mock_chain):
        """Test that RetryableChain works for successful chains."""
        retryable_chain = RetryableChain(mock_chain)
        result = retryable_chain.invoke({"input": "test"})
        
        assert result == "chain result"
        mock_chain.invoke.assert_called_once_with({"input": "test"})
    
    @patch('time.sleep')
    def test_retryable_chain_with_failures(self, mock_sleep, mock_chain):
        """Test that RetryableChain retries on failures."""
        # Make the first call fail, second succeed
        mock_chain.invoke.side_effect = [
            RateLimitError(
                message="Rate limit reached. Please try again in 1s.",
                response=Mock(status_code=429),
                body={"error": {"code": "rate_limit_exceeded"}}
            ),
            "success after retry"
        ]
        
        retryable_chain = RetryableChain(mock_chain, max_retries=2, base_delay=0.1)
        result = retryable_chain.invoke({"input": "test"})
        
        assert result == "success after retry"
        assert mock_chain.invoke.call_count == 2
        assert mock_sleep.call_count == 1
    
    def test_retryable_chain_attribute_delegation(self, mock_chain):
        """Test that RetryableChain delegates attributes to the wrapped chain."""
        mock_chain.some_attribute = "test_value"
        mock_chain.some_method = Mock(return_value="method_result")
        
        retryable_chain = RetryableChain(mock_chain)
        
        # Test attribute access
        assert retryable_chain.some_attribute == "test_value"
        
        # Test method access
        result = retryable_chain.some_method("arg")
        assert result == "method_result"
        mock_chain.some_method.assert_called_once_with("arg")


class TestRetryLLMCall:
    """Test the retry_llm_call convenience function."""
    
    @patch('time.sleep')
    def test_retry_llm_call_success(self, mock_sleep):
        """Test that retry_llm_call works for successful functions."""
        def successful_function(arg1, arg2, kwarg1=None):
            return f"result: {arg1}, {arg2}, {kwarg1}"
        
        result = retry_llm_call(successful_function, "a", "b", kwarg1="c", max_retries=3)
        assert result == "result: a, b, c"
        assert mock_sleep.call_count == 0  # No retries needed
    
    @patch('time.sleep')
    def test_retry_llm_call_with_retries(self, mock_sleep, mock_failing_function):
        """Test that retry_llm_call retries on failures."""
        failing_func = mock_failing_function(fail_count=1, success_result="final result")
        
        result = retry_llm_call(failing_func, max_retries=3)
        assert result == "final result"
        assert failing_func.call_count["count"] == 2  # Failed once, succeeded on second
        assert mock_sleep.call_count == 1


@pytest.mark.integration
class TestRetryIntegration:
    """Integration tests for retry mechanism with actual LLM components (mocked)."""
    
    @patch('resumetailor.services.retry.time.sleep')
    def test_resume_writer_with_retry(self, mock_sleep):
        """Test that ResumeWriter uses retry mechanism correctly."""
        from resumetailor.services.retry import RetryableChain
        
        # Create a mock chain that fails once then succeeds
        mock_chain = Mock()
        mock_chain.invoke.side_effect = [
            RateLimitError(
                message="Rate limit reached. Please try again in 2s.",
                response=Mock(status_code=429),
                body={"error": {"code": "rate_limit_exceeded"}}
            ),
            {"section_data": [{"title": "Test"}], "explanation": "Test explanation"}
        ]
        
        retryable_chain = RetryableChain(mock_chain)
        result = retryable_chain.invoke({"test": "data"})
        
        assert result == {"section_data": [{"title": "Test"}], "explanation": "Test explanation"}
        assert mock_chain.invoke.call_count == 2
        assert mock_sleep.call_count == 1
    
    def test_retry_configuration_defaults(self):
        """Test that retry mechanism uses sensible defaults."""
        from resumetailor.services.retry import RetryableChain, DEFAULT_MAX_RETRIES
        
        mock_chain = Mock()
        retryable_chain = RetryableChain(mock_chain)
        
        assert retryable_chain.max_retries == DEFAULT_MAX_RETRIES
        assert retryable_chain.base_delay == 1.0
        assert retryable_chain.max_delay == 300.0
        assert retryable_chain.backoff_factor == 2.0
        assert retryable_chain.jitter is True


@pytest.mark.performance
class TestRetryPerformance:
    """Performance tests for retry mechanism."""
    
    @patch('time.sleep')  # Mock sleep to avoid actual delays in tests
    def test_retry_timing_accuracy(self, mock_sleep):
        """Test that retry delays are calculated accurately."""
        @retry_with_exponential_backoff(
            max_retries=3,
            base_delay=1.0,
            backoff_factor=2.0,
            jitter=False  # Disable jitter for predictable timing
        )
        def always_failing_function():
            raise RateLimitError(
                message="Always fails",
                response=Mock(status_code=429),
                body={"error": {"code": "rate_limit_exceeded"}}
            )
        
        with pytest.raises(RateLimitError):
            always_failing_function()
        
        # Check that sleep was called with expected delays: 1.0, 2.0, 4.0
        sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
        expected_delays = [1.0, 2.0, 4.0]
        assert sleep_calls == expected_delays
    
    @patch('time.sleep')
    def test_max_retry_limit_enforcement(self, mock_sleep):
        """Test that max retry limit is strictly enforced."""
        max_retries = 2
        
        @retry_with_exponential_backoff(max_retries=max_retries, base_delay=0.1)
        def always_failing_function():
            raise APIConnectionError(request=Mock())
        
        with pytest.raises(APIConnectionError):
            always_failing_function()
        
        # Should sleep exactly max_retries times
        assert mock_sleep.call_count == max_retries