from gshock_api.logger import logger

class UnknownIO:
    @staticmethod
    def on_received(message):
        logger.info(f"UnknownIO onReceived: {message}")
