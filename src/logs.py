import subprocess
import multiprocessing
from multiprocessing.connection import Connection


def read_logs_and_send(pipe_conn: Connection, command: str) -> None:
    with subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    ) as process:
        if process.stdout is None:
            return

        for line in process.stdout:
            pipe_conn.send(line.strip())  # Send each line of log

    pipe_conn.close()
