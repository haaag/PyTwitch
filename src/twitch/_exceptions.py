from __future__ import annotations

import httpx


class EnvValidationError(Exception):
    pass


class ExecutableNotFoundError(Exception):
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
)
