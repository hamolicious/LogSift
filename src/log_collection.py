from collections.abc import Callable
import multiprocessing
import multiprocessing.connection
import subprocess
from .log import Log
from multiprocessing.connection import Connection
import threading


def read_logs_and_send(pipe_conn: Connection, command: str) -> None:
    with subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ) as process:
        if process.stdout is None:
            return

        for line in process.stdout:
            pipe_conn.send(line.strip())

    pipe_conn.close()


class LogManager:
    MAX_BUFFERED_LOGS = 1000

    def __init__(self, command: str, log_callback: Callable) -> None:
        self._command = command
        self.ingest_logs = True
        self.log_callback: Callable = log_callback

        self._running = True

    def set_command(self, command: str) -> None:
        self._command = command

    def run(self) -> None:
        command_process, pipe = self._setup_command_in_background()

        log_collection_thread = threading.Thread(
            target=self._worker,
            args=(
                command_process,
                pipe,
            ),
            daemon=True,
        )

        command_process.start()
        log_collection_thread.start()

    def _setup_command_in_background(
        self,
    ) -> tuple[multiprocessing.Process, multiprocessing.connection.Connection]:
        # TODO: implement ingesting logs via piped command
        # TODO: implement run command via UI
        parent_conn, child_conn = multiprocessing.Pipe()
        process = multiprocessing.Process(
            target=read_logs_and_send,
            args=(child_conn, self._command),
            daemon=True,
        )
        self.logs_process = process

        return process, parent_conn

    def stop(self) -> None:
        self._running = False

        self.logs_process.terminate()
        self.logs_process.join()
        self.logs_process.close()

    def _worker(
        self,
        process: multiprocessing.Process,
        connection: multiprocessing.connection.Connection,
    ) -> None:
        buffer: list[Log] = []

        # TODO: how do I force-trigger this when ingest logs is toggled on?
        # currently: need to wait for a new log to flush buffer
        while process.is_alive() or connection.poll():
            if not connection.poll():
                continue

            log_line = connection.recv()

            if len(buffer) > self.MAX_BUFFERED_LOGS:
                buffer.pop(0)

            buffer.append(Log(log_line))

            if not self.ingest_logs:
                continue

            for log in buffer:
                self.log_callback(log)

            buffer = []
