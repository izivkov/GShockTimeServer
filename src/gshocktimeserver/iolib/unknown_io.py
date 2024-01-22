class UnknownIO:
    @staticmethod
    def on_received(message):
        logger.info(f"UnknownIO onReceived: {message}")
