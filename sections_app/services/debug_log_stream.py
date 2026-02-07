import logging
import threading
from typing import List

_MAX_LOG_LINES = 2000

_LOG_BUFFER: List[str] = []
_LOCK = threading.Lock()


class InMemoryLogHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
        except Exception:
            msg = record.getMessage()
        with _LOCK:
            _LOG_BUFFER.append(msg)
            if len(_LOG_BUFFER) > _MAX_LOG_LINES:
                del _LOG_BUFFER[: len(_LOG_BUFFER) - _MAX_LOG_LINES]


def get_log_buffer() -> List[str]:
    with _LOCK:
        return list(_LOG_BUFFER)


def get_in_memory_handler() -> InMemoryLogHandler:
    handler = InMemoryLogHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    return handler


# Helper to append an arbitrary message at a given severity to the buffer
def emit_to_in_memory_buffer(level: int, msg: str) -> None:
    handler = get_in_memory_handler()
    record = logging.LogRecord("notification", level, __file__, 1, msg, (), None)
    handler.emit(record)
