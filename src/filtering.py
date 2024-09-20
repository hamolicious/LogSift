from .term_decoder import TermDecoder


class FilterManager:
    decoder = TermDecoder()

    def __init__(self) -> None:
        self._filter = ""

        self._filter_active: bool = True
        self._case_insensitive: bool = True
        self._match_all: bool = False

    @property
    def is_disabled(self) -> bool:
        return (
            not self._filter_active
            or self.filter == ""
            or len(self.decode()) == 0
            or self.decode()[0] == ""
        )

    @property
    def filter(self):
        return self._filter

    def validate(self, override_filter: str | None = None) -> bool:
        try:
            self.decoder.run(override_filter or self.filter)
            return True
        except ValueError:
            return False

    def set_filter(self, filter_: str) -> bool:
        self._filter = filter_
        return self.validate()

    @property
    def match_all(self):
        return self._match_all

    def set_match_all(self, value: bool) -> None:
        self._match_all = value

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

    def handle_case_sensitivity(self, value: str) -> str:
        return value.lower() if self.case_insensitive else value

    def decode(self) -> list[str]:
        terms = []
        try:
            terms = self.decoder.run(self.filter)
        except ValueError:
            terms = self.decoder.run(self.filter + '"')

        return terms

    def match(self, log_line: str) -> bool:
        if self.is_disabled:
            return True

        terms = self.decode()

        def _match_term(term: str) -> bool:
            inverted = term.startswith("!")
            matcher = self.handle_case_sensitivity(term[1::] if inverted else term)

            value = matcher in self.handle_case_sensitivity(log_line)

            return (not value) if inverted else value

        if self.match_all:
            return all(map(_match_term, terms))

        return any(map(_match_term, terms))
