from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, Center
from textual.widgets import (
    RichLog,
    Input,
    Label,
    RadioButton,
    Rule,
    RadioSet,
)


import multiprocessing


from src.components.spacer import Spacer
from src.log import Log
from src.logs import read_logs_and_send
from src.filtering import FilterManager
from src.types.ids import Ids


class LoggerApp(App):
    """Logging tool"""

    CSS_PATH = "src/css/app.tcss"

    BINDINGS = [
        Binding("s", action=f"focus('#{Ids.FILTER}')"),
        Binding("p", action=f"toggle_setting('#{Ids.INGEST_LOGS_TOGGLE}')"),
        Binding("f", action=f"toggle_setting('#{Ids.FILTER_TOGGLE}')"),
        Binding("m", action=f"toggle_setting('#{Ids.MATCH_ALL}')"),
        Binding("c", action=f"toggle_setting('#{Ids.CASE_INSENSITIVE_TOGGLE}')"),
        Binding("o", action=f"toggle_setting('#{Ids.FILTER_OMIT}')"),
        Binding("l", action=f"toggle_setting('#{Ids.FILTER_HIGHLIGHT}')"),
        Binding("b", action=f"toggle_visible('#{Ids.SETTINGS_CONTAINER}')"),
    ]

    ingest_logs = True

    all_ingested_logs: list[Log] = []
    filtered_logs: list[Log] = []

    filter_manager = FilterManager()
    filter_mode = Ids.FILTER_OMIT

    MAX_INGESTED_LOGS = 100_000
    MAX_DISPLAY_LOGS = 100
    MAX_BUFFERED_LOGS = 500

    def action_toggle_visible(self, selector: str) -> None:
        self.query_one(selector).toggle_class("hidden")

    def action_toggle_setting(self, selector: str) -> None:
        self.query_one(selector, RadioButton).toggle()

    async def action_focus(self, selector: str) -> None:
        self.query_one(selector).focus()

    def ingest_log(self, log: str | Log) -> None:
        if isinstance(log, str):
            log = Log(log)

        if len(self.all_ingested_logs) > self.MAX_INGESTED_LOGS:
            self.all_ingested_logs.pop(0)

        self.all_ingested_logs.append(log)
        self.filter_and_refresh_logs()

    def add_to_logger(self, log_line: str) -> None:
        logger = self.query_one(f"#{Ids.LOGGER}", RichLog)
        logger.write(log_line)

    def clear_logger(self) -> None:
        logger = self.query_one(f"#{Ids.LOGGER}", RichLog)
        logger.clear()

    def filter_and_refresh_logs(self) -> None:
        if self.filter_mode == Ids.FILTER_OMIT:
            self.filter_using_omit()

        elif self.filter_mode == Ids.FILTER_HIGHLIGHT:
            self.filter_using_highlight()

        else:
            raise ValueError(f"No filter mode for {self.filter_mode=}")

        self.refresh_logger()

    def filter_using_omit(self) -> None:
        self.filtered_logs = list(
            filter(
                lambda log: self.filter_manager.match(log.text),
                self.all_ingested_logs,
            )
        )

    def filter_using_highlight(self) -> None:
        logs: list[Log] = []
        for log in self.all_ingested_logs:
            log_copy = log.copy()
            logs.append(log_copy)

            if (
                self.filter_manager.match(log.text)
                and not self.filter_manager.is_disabled
            ):
                log_copy.set_prefix("[on #006000]")
                log_copy.set_suffix("[/on #006000]")
                continue

        self.filtered_logs = logs

    def refresh_logger(self) -> None:
        self.clear_logger()
        for log in self.filtered_logs:
            self.add_to_logger(str(log))

    @work(thread=True)
    def start_updating_logs(self) -> None:
        parent_conn, child_conn = multiprocessing.Pipe()

        # TODO: implement ingesting logs via piped command
        # TODO: implement run command via UI
        # TODO: implement run command via arg
        command = "tail -f /var/log/syslog"
        process = multiprocessing.Process(
            target=read_logs_and_send, args=(child_conn, command)
        )
        process.start()

        buffer: list[Log] = []

        # TODO: how do I force-trigger this when ingest logs is toggled on?
        # currently: need to wait for a new log to flush buffer
        while process.is_alive() or parent_conn.poll():
            if not parent_conn.poll():
                continue

            log_line = parent_conn.recv()

            if len(buffer) > self.MAX_BUFFERED_LOGS:
                buffer.pop(0)

            buffer.append(Log(log_line))

            if not self.ingest_logs:
                continue

            for log in buffer:
                self.ingest_log(log)

            buffer = []

        process.join()

    @on(Input.Changed)
    def on_input_changed(self, event: Input.Changed) -> None:
        self.filter_manager.set_filter(event.value)
        self.filter_and_refresh_logs()

    @on(RadioButton.Changed)
    @on(RadioSet.Changed)
    def on_radio_button_changed(
        self, event: RadioButton.Changed | RadioSet.Changed
    ) -> None:
        id_: str | None
        value: bool

        if isinstance(event, RadioSet.Changed):
            id_ = event.pressed.id
            value = event.pressed.value
        else:
            id_ = event.radio_button.id
            value = event.radio_button.value

        refilter = True

        match id_:
            case Ids.INGEST_LOGS_TOGGLE:
                self.ingest_logs = value
                refilter = value is True

            case Ids.FILTER_TOGGLE:
                self.filter_manager.filter_active = value

            case Ids.CASE_INSENSITIVE_TOGGLE:
                self.filter_manager.case_insensitive = value

            case Ids.FILTER_HIGHLIGHT:
                self.filter_mode = id_

            case Ids.FILTER_OMIT:
                self.filter_mode = id_

            case Ids.MATCH_ALL:
                self.filter_manager.set_match_all(value)

            case _:
                raise ValueError(f"No case for {id_}")

        if refilter:
            self.filter_and_refresh_logs()

    def on_mount(self) -> None:
        self.start_updating_logs()

    def compose(self) -> ComposeResult:
        with Horizontal(id="app-container"):
            with Vertical(id="logger-container"):
                yield RichLog(
                    highlight=True,
                    markup=True,
                    wrap=False,
                    max_lines=self.MAX_DISPLAY_LOGS,
                    id=Ids.LOGGER,
                )
                yield Input(
                    placeholder="Filter",
                    id=Ids.FILTER,
                    tooltip="(s) Filter logs\n- terms are separated by space\n- use '!' to invert terms",
                )

            with Container(id=Ids.SETTINGS_CONTAINER):
                with Center():
                    yield Label("Filtering")
                yield Rule()

                yield Label("Ingestion Settings")

                yield RadioButton(
                    "Ingest logs",
                    value=True,
                    id=Ids.INGEST_LOGS_TOGGLE,
                    classes="settings-radio-button",
                    tooltip="(p) Toggle ingestion of logs, while off, the app still buffers incoming logs and will flush that buffer once re-enabled.",
                )

                yield Spacer()
                yield Label("Filter Settings")

                yield RadioButton(
                    "Filter Active",
                    value=True,
                    id=Ids.FILTER_TOGGLE,
                    classes="settings-radio-button",
                    tooltip="(f) Toggle enforcing filter",
                )
                yield RadioButton(
                    "Match All",
                    value=False,
                    id=Ids.MATCH_ALL,
                    classes="settings-radio-button",
                    tooltip="(m) Matches either all or at least 1 term from filter",
                )
                yield RadioButton(
                    "Case insensitive",
                    value=True,
                    id=Ids.CASE_INSENSITIVE_TOGGLE,
                    classes="settings-radio-button",
                    tooltip="(c) Toggle case sensitivity/insensitivity",
                )

                yield Spacer()
                yield Label("Filter Mode")

                with RadioSet(classes="settings-radio-button"):
                    yield RadioButton(
                        "Omit",
                        value=True,
                        id=Ids.FILTER_OMIT,
                        classes="full-width",
                        tooltip="(o) Omit non-matching logs",
                    )
                    yield RadioButton(
                        "Highlight",
                        id=Ids.FILTER_HIGHLIGHT,
                        classes="full-width",
                        tooltip="(l) Highlight matching logs",
                    )


if __name__ == "__main__":
    app = LoggerApp()
    app.run()
