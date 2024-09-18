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


class LoggerApp(App):
    """Logging tool"""

    log_pos_pointer = 0
    logs: list[Log] = []
    filtered_logs: list[Log] = []
    current_filter: str = ""

    def filter_logs(self) -> None:
        if self.current_filter.strip() == "":
            self.filtered_logs = self.logs
        else:
            self.filtered_logs = list(
                filter(lambda log: self.current_filter in log.text, self.logs)
            )

        logger = self.query_one("#logger", RichLog)
        logger.clear()

        for log in self.filtered_logs:
            logger.write(log.text)

    @work(thread=True)
    def start_updating_logs(self) -> None:
        logger = self.query_one("#logger", RichLog)

        parent_conn, child_conn = multiprocessing.Pipe()
        command = "tail -f /var/log/syslog"
        process = multiprocessing.Process(
            target=read_logs_and_send, args=(child_conn, command)
        )
        process.start()

        # Receive and print logs in the parent process
        while process.is_alive() or parent_conn.poll():  # Check for data in pipe
            if parent_conn.poll():  # If there's data to receive
                log_line = parent_conn.recv()
                logger.write(log_line)
                self.logs.append(Log(log_line))

        process.join()

    @on(Input.Changed)
    def on_input_changed(self, event: Input.Changed) -> None:
        self.current_filter = event.value
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
