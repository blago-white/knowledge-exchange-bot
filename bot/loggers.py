import logging
import datetime


class ConsoleDebugLogger(logging.Handler):
    def emit(self, record):
        print(f"{datetime.datetime.now()} {record.getMessage()}")
