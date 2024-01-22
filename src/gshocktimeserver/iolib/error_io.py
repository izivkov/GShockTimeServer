from logger import logger


class ErrorIO:
    @staticmethod
    async def on_received(message):
        logger.info(f"ErrorIO onReceived: {message}")
