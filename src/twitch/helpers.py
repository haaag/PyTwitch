# utils.py

from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict
from functools import wraps
from pathlib import Path
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


def astimeit(func: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(func)
    async def timeit_wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        result = await func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        logging.info(f'async {func.__name__}: took {total_time:.4f} seconds')
        return result

    return timeit_wrapper


def logme(message: str) -> Callable[..., Any]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            logging.info(f'{func.__name__}: {message}')
            return func(*args, **kwargs)

        return wrapper

    return decorator


def savetojson(filename: str, data: dict[str, Any]) -> None:
    file = Path('~/dev/git/python/pytwitch/assets').expanduser() / filename

    if not file.exists():
        file.touch()

    result = [asdict(d) for d in data.values()]
    with file.open(mode='w') as f:
        json.dump(result, f, indent=4)
