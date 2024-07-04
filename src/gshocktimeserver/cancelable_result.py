import asyncio
from typing import Any

class CancelableResult:
    def __init__(self, timeout: float = 5.0):
        self._timeout = timeout
        self._future: asyncio.Future[Any] = asyncio.Future()

    async def get_result(self) -> Any:
        try:
            return await asyncio.wait_for(self._future, timeout=self._timeout)
        except asyncio.TimeoutError:
            if not self._future.done():
                self._future.set_result('')
            return await self._future

    def set_result(self, result: Any) -> None:
        if not self._future.done():
            self._future.set_result(result)

# Example usage
async def main():
    cancelable_result = CancelableResult(timeout=5)

    # Simulate some async work that might or might not set a result
    async def some_async_work():
        await asyncio.sleep(3)  # Change this to 6 to test the timeout
        cancelable_result.set_result('Result after async work')

    await asyncio.gather(some_async_work(), asyncio.sleep(6))

    final_result = await cancelable_result.get_result()
    print(f'Final result: "{final_result}"')

# Run the main coroutine
# asyncio.run(main())

cancelable_result = CancelableResult()
