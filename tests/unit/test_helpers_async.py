"""
Unittests voor async helperfuncties: retries, timeouts, async utilities.
"""
import pytest
import time

def async_parametrize(*args, **kwargs):
    """Custom parametrize decorator voor async tests."""
    return pytest.mark.parametrize(*args, **kwargs)

# Performance testing decorator
def performance_test(max_time: float = 5.0):
    """Decorator voor performance testing van async functies."""
    def decorator(func):
        @pytest.mark.asyncio
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            assert execution_time < max_time, f"Test took {execution_time:.3f}s, expected < {max_time}s"
            return result
        return wrapper
    return decorator 