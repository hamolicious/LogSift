from textual import events, on, work
from textual.app import App, ComposeResult
from textual.css.query import NoMatches
from textual.reactive import var
from textual.containers import Container, Horizontal, Vertical, Center
from textual.widgets import (
    Button,
    Digits,
    RichLog,
    Input,
    Label,
    RadioButton,
    Rule,
    RadioSet,
)

import os
import time
import datetime
import sys

import subprocess
import multiprocessing
from multiprocessing.connection import Connection


from src.log import Log
from src.logs import read_logs_and_send
from src.filtering import FilterManager
from src.types.ids import Ids


class LoggerApp(App):
    """Logging tool"""

    CSS_PATH = "src/css/app.tcss"

    ingest_logs = True

    log_pos_pointer = 0
    all_ingested_logs: list[Log] = []
    filtered_logs: list[Log] = []

    filter_manager = FilterManager()

    MAX_LOGS = 10_000
    MAX_LOG_BUFFER_LEN = 500

    def ingest_log(self, log: str | Log) -> None:
        if isinstance(log, str):
            log = Log(log)

        if len(self.all_ingested_logs) > self.MAX_LOGS:
            self.all_ingested_logs.pop(0)

        self.all_ingested_logs.append(log)
        self.filter_and_refresh_logs()

    def add_to_logger(self, log_line: str) -> None:
        logger = self.query_one("#logger", RichLog)
        logger.write(log_line)

    def clear_logger(self) -> None:
        logger = self.query_one("#logger", RichLog)
        logger.clear()

    def filter_and_refresh_logs(self) -> None:
        self.filtered_logs = list(
            filter(
                lambda log: self.filter_manager.match(log.text),
                self.all_ingested_logs,
            )
        )
        self.refresh_logger()

    def refresh_logger(self) -> None:
        self.clear_logger()
        for log in self.filtered_logs:
            self.add_to_logger(log.text)

    @work(thread=True)
    def start_updating_logs(self) -> None:
        parent_conn, child_conn = multiprocessing.Pipe()
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

            if len(buffer) > self.MAX_LOG_BUFFER_LEN:
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
    def on_radio_button_changed(self, event: RadioButton.Changed) -> None:
        id_ = event.radio_button.id
        value = event.radio_button.value

        refilter = False

        match id_:
            case Ids.INGEST_LOGS_TOGGLE:
                self.ingest_logs = value
                refilter = value is True

            case Ids.FILTER_TOGGLE:
                self.filter_manager.filter_active = value
                refilter = True

            case Ids.CASE_INSENSITIVE_TOGGLE:
                self.filter_manager.case_insensitive = value
                refilter = True

            case _:
                raise ValueError(f"No case for {id_}")

        if refilter:
            self.filter_and_refresh_logs()

    def on_mount(self) -> None:
        self.start_updating_logs()

    def compose(self) -> ComposeResult:
        with Horizontal(id="app-container"):
            with Vertical(id="logger-container"):
                yield RichLog(highlight=True, markup=True, wrap=False, id="logger")
                yield Input(id="filter")

            with Container(id="settings-container"):
                with Center():
                    yield Label("Filtering")
                yield Rule()

                yield RadioButton("Ingest logs", value=True, id=Ids.INGEST_LOGS_TOGGLE)
                yield RadioButton("Filter", value=True, id=Ids.FILTER_TOGGLE)
                yield RadioButton(
                    "Case sensitive", value=True, id=Ids.CASE_INSENSITIVE_TOGGLE
                )


if __name__ == "__main__":
    app = LoggerApp()
    app.run()
