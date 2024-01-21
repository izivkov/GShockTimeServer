class ErrorIO:
    @staticmethod
    async def on_received(message):
        print(f"ErrorIO onReceived: {message}")
