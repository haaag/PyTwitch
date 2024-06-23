# utils.py

from __future__ import annotations

import logging
import time
from functools import wraps
from typing import Any
from typing import Callable

logger = logging.getLogger(__name__)


def timeit(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    def timeit_wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        logging.info(f'{func.__name__}: {args=} {kwargs=} Took {total_time:.4f} seconds')
        return result

    return timeit_wrapper


def logme(message):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logging.info(f'{func.__name__}: {message}')
            return func(*args, **kwargs)

        return wrapper

    return decorator
