class FilterManager:
    def __init__(self) -> None:
        self._filter = ""

        self._filter_active: bool = True
        self._case_insensitive: bool = True

    @property
    def filter(self):
        return self._filter

    def set_filter(self, filter_: str) -> None:
        self._filter = filter_

    @property
    def filter_active(self) -> bool:
        return self._filter_active

    @filter_active.setter
    def filter_active(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise ValueError("Filter active must be a boolean")
        self._filter_active = value

    @property
    def case_insensitive(self) -> bool:
        return self._case_insensitive

    @case_insensitive.setter
    def case_insensitive(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise ValueError("Case insensitive must be a boolean")
        self._case_insensitive = value

    def match(self, log_line: str) -> bool:
        if self.filter == "" or not self.filter_active:
            return True

        if self.case_insensitive:
            return self.filter.lower() in log_line.lower()

        return self.filter in log_line
