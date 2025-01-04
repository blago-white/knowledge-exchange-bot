import logging


class ConsoleDebugLogger(logging.Handler):
    def emit(self, record):
        print(record.getMessage())
