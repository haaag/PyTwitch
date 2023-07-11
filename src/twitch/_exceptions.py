from __future__ import annotations

import httpx


class ValidationEnvError(Exception):
    pass


class ExecutableNotFoundError(Exception):
    pass


CONNECTION_EXCEPTION = (httpx.ConnectError, httpx.HTTPStatusError)
EXCEPTIONS = (ExecutableNotFoundError, ValidationEnvError)
