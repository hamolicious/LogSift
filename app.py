import os
import platform
from typing import Literal, Never
from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, Center
from textual.widgets import (
    RichLog,
    Button,
    Input,
    Label,
    RadioButton,
    Rule,
    RadioSet,
)


import multiprocessing
import tempfile


from src.components.spacer import Spacer
from src.components.keybinds import KeybindsInfo
from src.log import Log
from src.logs import read_logs_and_send
from src.filtering import FilterManager
from src.types.ids import Ids
from src.args import get_args
from src.bindings import BINDINGS as DEFAULT_BINDINGS


class LoggerApp(App):
    """Logging tool"""

    CSS_PATH = "src/css/app.tcss"
    BINDINGS = list(DEFAULT_BINDINGS)  # to make mypy happy :/

    command = get_args()

    ingest_logs = True
    logs_process: multiprocessing.Process | None

    all_ingested_logs: list[Log] = []
    filtered_logs: list[Log] = []

    filter_manager = FilterManager()
    filter_mode = Ids.FILTER_OMIT

    MAX_INGESTED_LOGS = 100_000
    MAX_DISPLAY_LOGS = 500
    MAX_BUFFERED_LOGS = 500

    def action_refresh_logger(self) -> None:
        self.refresh_logger()

    def action_toggle_visible(self, selector: str) -> None:
        self.query_one(selector).toggle_class("hidden")

    @work
    async def action_show_help(self) -> None:
        # probably a better way of doing it
        await self.run_action(f"toggle_setting('#{Ids.PAUSE_DISPLAYING_LOGS_TOGGLE}')")
        await self.push_screen_wait(KeybindsInfo(self.BINDINGS))
        await self.run_action(f"toggle_setting('#{Ids.PAUSE_DISPLAYING_LOGS_TOGGLE}')")

    def action_toggle_setting(self, selector: str) -> None:
        self.query_one(selector, RadioButton).toggle()

    def action_copy_shown(self) -> None:
        logs = (
            self.all_ingested_logs
            if self.filter_manager.is_disabled
            else self.filtered_logs
        )
        text = "\n".join(map(str, logs))
        current_os = platform.platform(aliased=True, terse=True)
        path = tempfile.mktemp()

        with open(path, "w") as f:
            f.write(text)

        if "Linux" in current_os:
            os.system(f"cat {path} | xclip -sel clip")
        elif "MacOS" in current_os:
            os.system(f"cat {path} | pbcopy")
        else:
            raise NotImplementedError(f"Copying not implemented for {current_os=}")

        os.remove(path)

    def action_scroll_logger(
        self, direction: Literal["up", "down", "fup", "fdown"]
    ) -> None:
        def repeat(f, n):
            return [f() in range(n)]

        logger = self.query_one(f"#{Ids.LOGGER}", RichLog)

        match direction:
            case "up":
                logger.scroll_up()
            case "down":
                logger.scroll_down()
            case "fup":
                repeat(logger.scroll_up, 10)
            case "fdown":
                repeat(logger.scroll_down, 10)
            case _:
                raise ValueError(f"no case for direction {direction}")

    async def action_focus(self, selector: str) -> None:
        self.query_one(selector).focus()

    def ingest_log(self, log: str | Log) -> None:
        if isinstance(log, str):
            log = Log(log)

        if len(self.all_ingested_logs) > self.MAX_INGESTED_LOGS:
            self.all_ingested_logs.pop(0)

        self.all_ingested_logs.append(log)

        self.update_log_count()

        if not self.filter_manager.match(str(log)):
            return

        self.add_to_logger(str(log))
        # self.filter_and_refresh_logs()

    def add_to_logger(self, log_line: str) -> None:
        logger = self.query_one(f"#{Ids.LOGGER}", RichLog)
        logger.write(log_line)

    def clear_logger(self) -> None:
        logger = self.query_one(f"#{Ids.LOGGER}", RichLog)
        logger.clear()

    def refresh_logger(self, clear: bool = False) -> None:
        if clear:
            self.clear_logger()

        for log in self.filtered_logs[-self.MAX_DISPLAY_LOGS : :]:
            self.add_to_logger(str(log))

    @work(thread=True, exclusive=True)
    def filter_and_refresh_logs(self) -> None:
        if self.filter_mode == Ids.FILTER_OMIT:
            self.filter_using_omit()

        elif self.filter_mode == Ids.FILTER_HIGHLIGHT:
            self.filter_using_highlight()

        else:
            raise ValueError(f"No filter mode for {self.filter_mode=}")

        self.update_filtered_log_count()
        self.refresh_logger(clear=True)

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

    def update_log_count(self) -> None:
        label = self.query_one("#" + Ids.LOGS_COUNT, Label)

        label._renderable = f"{len(self.all_ingested_logs):,} Logs Ingested"
        label.refresh()

    def update_filtered_log_count(self) -> None:
        label = self.query_one("#" + Ids.FILTERED_LOGS_COUNT, Label)

        count = 0
        if not self.filter_manager.is_disabled:
            count = len(self.filtered_logs)

        label._renderable = f"{count:,} Filtered Logs"
        label.refresh()

    @work(thread=True, exclusive=True)
    def start_updating_logs(self) -> None:
        if self.command is None:
            return

        # TODO: implement ingesting logs via piped command
        # TODO: implement run command via UI
        parent_conn, child_conn = multiprocessing.Pipe()
        process = multiprocessing.Process(
            target=read_logs_and_send,
            args=(child_conn, self.command),
            daemon=True,
        )
        self.logs_process = process
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

    @on(Input.Changed)
    def on_input_changed(self, event: Input.Changed) -> None:
        self.filter_manager.set_filter(event.value)
        self.filter_and_refresh_logs()

    @on(Button.Pressed)
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        match event.button.id:
            case Ids.HELP_BUTTON:
                await self.run_action("show_help")
            case _:
                raise ValueError(f"no button handler for case: {Ids.HELP_BUTTON}")

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
            case Ids.PAUSE_DISPLAYING_LOGS_TOGGLE:
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

    def on_exit_app(self) -> None:
        if self.logs_process is None:
            return

        self.logs_process.terminate()
        self.logs_process.join(1)
        self.logs_process.close()

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

                with Horizontal(id=Ids.FILTER_CONTAINER):
                    yield Input(
                        placeholder="Filter",
                        id=Ids.FILTER,
                        tooltip="(f) Filter logs\n- terms are separated by space\n- use '!' to invert terms",
                    )

                    yield Button(
                        "?",
                        variant="primary",
                        id=Ids.HELP_BUTTON,
                        tooltip="(shift+h) Open help panel",
                    )

            with Container(id=Ids.SETTINGS_CONTAINER, classes="hidden"):
                with Center():
                    yield Label("Info", classes="title")
                yield Rule()

                yield Label("0 Logs Ingested", id=Ids.LOGS_COUNT, classes="full-width")
                yield Label(
                    "0 Filtered Logs", id=Ids.FILTERED_LOGS_COUNT, classes="full-width"
                )

                yield Spacer()
                with Center():
                    yield Label("Filtering", classes="title")
                yield Rule()

                yield Label("Ingestion Settings")

                yield RadioButton(
                    "Pause displaying logs",
                    value=True,
                    id=Ids.PAUSE_DISPLAYING_LOGS_TOGGLE,
                    classes="settings-radio-button",
                    tooltip="(p) Pauses logs being added to the logger window",
                )

                yield Spacer()
                yield Label("Filter Settings")

                yield RadioButton(
                    "Filter Active",
                    value=True,
                    id=Ids.FILTER_TOGGLE,
                    classes="settings-radio-button",
                    tooltip="(t) Toggle enforcing filter",
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
    # fix for macs
    multiprocessing.set_start_method("fork")

    app = LoggerApp()
    app.run()

    # release logs before exiting
    print("\n".join(map(str, app.all_ingested_logs)))
