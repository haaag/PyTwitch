from __future__ import annotations

import httpx
import tenacity


class EnvValidationError(Exception):
    pass


class ExecutableNotFoundError(Exception):
    pass


class ItemNotPlaylableError(Exception):
    pass


CONNECTION_EXCEPTION = (
    httpx.ConnectError,
    httpx.HTTPStatusError,
    httpx.ConnectTimeout,
)
EXCEPTIONS = (
    ExecutableNotFoundError,
    EnvValidationError,
    FileNotFoundError,
    NotImplementedError,
    ItemNotPlaylableError,
    tenacity.RetryError,
)
