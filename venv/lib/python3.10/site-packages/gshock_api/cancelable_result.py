import asyncio
from typing import Any
from gshock_api.exceptions import GShockConnectionError

class CancelableResult:
    def __init__(self, timeout: float = 10.0):
        self._timeout = timeout
        self._future: asyncio.Future[Any] = asyncio.Future()

    async def get_result(self) -> Any:
        try:
            result = await asyncio.wait_for(self._future, timeout=self._timeout)
            return result
        except asyncio.TimeoutError as e:
            if not self._future.done():
                self._future.set_result('')  # or raise an exception instead
            raise GShockConnectionError(f"Timeout occured waiting for response from the watch: {e}") from e

    def set_result(self, result: Any) -> None:
        if not self._future.done():
            self._future.set_result(result)

cancelable_result = CancelableResult()
