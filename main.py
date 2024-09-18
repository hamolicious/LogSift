import os
import time
import datetime
import sys
import threading


class Log:
    def __init__(self, text: str) -> None:
        self._text = text
        self._time = time.time()

    def __str__(self) -> str:
        t = datetime.datetime.fromtimestamp(self._time).strftime("%H:%M:%S.%f")[:-3]
        return f"[ {t} ] {self._text}"

    @property
    def text(self) -> str:
        return self._text

    @property
    def time(self) -> float:
        return self._time


class EnvironmentManager:
    terminal_width: int
    terminal_height: int


class ThreadHealthManager:
    display_thread: float = time.time()

    @classmethod
    def check_threads(cls) -> None:
        curr_time = time.time()
        if curr_time > cls.display_thread + 5:
            print("Display thread is not responding")


class LogsManager:
    _logs: list[Log] = []
    _lock = threading.Lock()

    @classmethod
    def get_logs(cls) -> list[Log]:
        with cls._lock:
            return cls._logs[::]

    @classmethod
    def add_entry(cls, log: Log | None) -> None:
        if log is None:
            return

        with cls._lock:
            cls._logs.append(log)

    @classmethod
    def get_len(cls) -> int:
        with cls._lock:
            return len(cls._logs)


def display_thread_worker() -> None:
    last_len = LogsManager.get_len()

    while True:
        ThreadHealthManager.display_thread = time.time()

        if last_len == LogsManager.get_len():
            continue

        clear_display()
        display_logs(LogsManager.get_logs())
        display_status(LogsManager.get_logs())

        last_len = LogsManager.get_len()


def get_log_line() -> Log | None:
    raw_line = sys.stdin.readline()
    log_line = raw_line

    return Log(log_line)


def clear_display() -> None:
    os.system("clear")


def display_logs(logs: list[Log], screen_buffer_len: int = 50) -> None:
    last_log: str = ""
    counter = 0

    for log in logs[-screen_buffer_len::]:
        if log.text == last_log and log.text.strip().lower() not in ["\n", "", "\t"]:
            counter += 1
            continue
        else:
            if counter > 0:
                print(f"\t+{counter} identical")
            counter = 0

        nl = ""
        if (
            log.text.endswith("\n")
            and len(log.text) > EnvironmentManager.terminal_width
        ):
            nl = "\n"

        print(str(log)[: EnvironmentManager.terminal_width :], end=nl)

        last_log = log.text


def display_status(logs: list[Log]) -> None:
    print()
    print(f"-= Supalogger captured {len(logs)} logs =-")


def start_display_thread() -> None:
    display_thread = threading.Thread(target=display_thread_worker)
    display_thread.daemon = True
    display_thread.start()


def update_environment() -> None:
    EnvironmentManager.terminal_width = os.get_terminal_size().columns
    EnvironmentManager.terminal_height = os.get_terminal_size().lines


def main() -> None:
    start_display_thread()

    while True:
        update_environment()

        log_line = get_log_line()
        LogsManager.add_entry(log_line)

        ThreadHealthManager.check_threads()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by user.")
