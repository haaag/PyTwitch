from __future__ import annotations

import httpx
import tenacity
from pyselector.key_manager import KeybindError


class EnvValidationError(Exception):
    pass


class ExecutableNotFoundError(Exception):
    pass


class ItemNotPlaylableError(Exception):
    pass


class ChannelOfflineError(Exception):
    pass


class InvalidConfigFileError(Exception):
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
    KeybindError,
    InvalidConfigFileError,
    ChannelOfflineError,
)
