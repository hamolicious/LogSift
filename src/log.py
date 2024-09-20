import time
import datetime


class Log:
    def __init__(self, text: str) -> None:
        self._text = text
        self._time = time.time()
        self._time_str = datetime.datetime.fromtimestamp(self._time).strftime(
            "%H:%M:%S.%f"
        )[:-3]

        self._prefix = ""
        self._suffix = ""

    def set_prefix(self, value: str):
        self._prefix = value

    def set_suffix(self, value: str):
        self._suffix = value

    @property
    def text(self) -> str:
        return self._text

    @property
    def time(self) -> float:
        return self._time

    @property
    def prefix(self) -> str:
        return self._prefix

    @property
    def suffix(self) -> str:
        return self._suffix

    def copy(self):
        copied_log = type(self)(self._text)
        copied_log._time = self._time

        return copied_log

    def __str__(self) -> str:
        return f"{self.prefix}{self._text}{self.suffix}"
