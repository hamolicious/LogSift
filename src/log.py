import time
import datetime
import dateutil
import dateutil.parser


class Log:
    def __init__(self, text: str) -> None:
        self._text = text

        self._ingest_time = time.time()
        self._time_ingest_str = datetime.datetime.fromtimestamp(
            self._ingest_time
        ).strftime("%H:%M:%S.%f")[:-3]

        self._prefix = ""
        self._suffix = ""

        self._stated_timestamp: float | None = None
        self._extract_data()

    def set_prefix(self, value: str):
        self._prefix = value

    def set_suffix(self, value: str):
        self._suffix = value

    @property
    def text(self) -> str:
        return self._text

    @property
    def time(self) -> float:
        return self._ingest_time

    @property
    def prefix(self) -> str:
        return self._prefix

    @property
    def suffix(self) -> str:
        return self._suffix

    def copy(self):
        copied_log = type(self)(self._text)
        copied_log._ingest_time = self._ingest_time

        return copied_log

    def __str__(self) -> str:
        return f"{self.prefix}{self._text}{self.suffix}"

    def _extract_timestamp(self) -> None:
        potential_stamps = self.text.split(" ")
        for stamp in potential_stamps:
            try:
                dt = dateutil.parser.isoparse(stamp).timestamp()
                self._stated_timestamp = dt
                return
            except ValueError:
                continue

    def _extract_data(self) -> None:
        self._extract_timestamp()
