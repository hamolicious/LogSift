from textual import events, on, work
from textual.app import App, ComposeResult
from textual.css.query import NoMatches
from textual.reactive import var
from textual.containers import Container
from textual.widgets import Button, Digits, RichLog, Input

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


class LoggerApp(App):
    """Logging tool"""

    log_pos_pointer = 0
    all_ingested_logs: list[Log] = []
    filtered_logs: list[Log] = []

    filter_manager = FilterManager()

    def filter_logs(self) -> None:
        if self.filter_manager.filter == "":
            self.filtered_logs = self.all_ingested_logs
        else:
            self.filtered_logs = list(
                filter(
                    lambda log: self.filter_manager.match(log.text),
                    self.all_ingested_logs,
                )
            )

        logger = self.query_one("#logger", RichLog)
        logger.clear()

        for log in self.filtered_logs:
            logger.write(log.text)

    def add_to_logger(self, log_line: str) -> None:
        logger = self.query_one("#logger", RichLog)
        logger.write(log_line)

    @work(thread=True)
    def start_updating_logs(self) -> None:
        parent_conn, child_conn = multiprocessing.Pipe()
        command = "tail -f /var/log/syslog"
        process = multiprocessing.Process(
            target=read_logs_and_send, args=(child_conn, command)
        )
        process.start()

        while process.is_alive() or parent_conn.poll():
            if parent_conn.poll():
                log_line = parent_conn.recv()

                self.all_ingested_logs.append(Log(log_line))
                if self.filter_manager.match(log_line):
                    self.filtered_logs.append(Log(log_line))
                    self.add_to_logger(log_line)

        process.join()

    @on(Input.Changed)
    def on_input_changed(self, event: Input.Changed) -> None:
        self.filter_manager.set_filter(event.value)
        self.filter_logs()

    def on_mount(self) -> None:
        self.start_updating_logs()

    def compose(self) -> ComposeResult:
        with Container(id="logger-container"):
            yield RichLog(highlight=True, markup=True, wrap=False, id="logger")
            yield Input(id="filter")


if __name__ == "__main__":
    app = LoggerApp()
    app.run()
