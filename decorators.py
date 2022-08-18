import time
import asyncio
from functools import wraps
from functools import lru_cache

def async_measure_time(func):
    @wraps(func)
    async def wrap(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        elapsed = time.perf.counter() - start
        print(f'Executed {func} in {elapsed:0.2f} seconds')
        return result
    return wrap

def measure_time(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf.counter() - start
        print(f'Executed {func} in {elapsed:0.2f} seconds')
        return result
    return wrap
        

              
