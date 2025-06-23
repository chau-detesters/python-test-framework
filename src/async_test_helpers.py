import asyncio
import time
from typing import Callable, Any, List, Dict
from contextlib import asynccontextmanager

"""
Helperfuncties voor asynchrone tests: wachten op condities, retries, performance meten.
"""

class AsyncTestHelper:
    """Helper utilities for async testing."""
    
    @staticmethod
    async def wait_for_condition(
        condition_func: Callable[[], bool],
        timeout: float = 10.0,
        interval: float = 0.1
    ) -> bool:
        """Wacht asynchroon tot een conditie True is of timeout bereikt is."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if await condition_func() if asyncio.iscoroutinefunction(condition_func) else condition_func():
                return True
            await asyncio.sleep(interval)
        
        return False
    
    @staticmethod
    async def retry_async(
        func: Callable,
        max_retries: int = 3,
        delay: float = 1.0,
        backoff_factor: float = 2.0
    ) -> Any:
        """Voer een async functie uit met retries en exponential backoff."""
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return await func()
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    await asyncio.sleep(delay * (backoff_factor ** attempt))
        
        raise last_exception
    
    @staticmethod
    async def measure_async_performance(func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Meet de wall time en CPU tijd van een async functie-uitvoering."""
        start_time = time.time()
        start_cpu = time.process_time()
        
        try:
            result = await func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
        
        end_time = time.time()
        end_cpu = time.process_time()
        
        return {
            "result": result,
            "success": success,
            "error": error,
            "wall_time": end_time - start_time,
            "cpu_time": end_cpu - start_cpu
        } 