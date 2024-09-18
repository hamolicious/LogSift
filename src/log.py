import time
import datetime


class Log:
    def __init__(self, text: str) -> None:
        self._text = text
        self._time = time.time()

    def __str__(self) -> str:
        t = datetime.datetime.fromtimestamp(self._time).strftime("%H:%M:%S.%f")[:-3]
        return f"[ {t} ] {self._text}"

    @property
    def text(self) -> str:
        return self._text

    @property
    def time(self) -> float:
        return self._time
