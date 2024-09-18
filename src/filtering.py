class FilterManager:
    def __init__(self) -> None:
        self._filter = ""

    @property
    def filter(self):
        return self._filter

    def match(self, log_line: str) -> bool:
        if self.filter == "":
            return True

        return self.filter in log_line

    def set_filter(self, filter_: str) -> None:
        self._filter = filter_
