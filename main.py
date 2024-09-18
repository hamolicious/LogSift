import os
import time
import sys
import threading


class Environment:
    terminal_width: int
    terminal_height: int


class ThreadLiveness:
    display_thread: float = time.time()

    @classmethod
    def check_threads(cls) -> None:
        curr_time = time.time()
        if curr_time > cls.display_thread + 5:
            print("Display thread is not responding")


class Logs:
    _logs: list[str] = []
    _lock = threading.Lock()

    @classmethod
    def get_logs(cls) -> list[str]:
        with cls._lock:
            return cls._logs[::]

    @classmethod
    def add_entry(cls, log: str | None) -> None:
        if log is None:
            return

        with cls._lock:
            cls._logs.append(log)

    @classmethod
    def get_len(cls) -> int:
        with cls._lock:
            return len(cls._logs)


def display_thread_worker() -> None:
    last_len = Logs.get_len()

    while True:
        ThreadLiveness.display_thread = time.time()

        if last_len == Logs.get_len():
            continue

        clear_display()
        display_logs(Logs.get_logs())
        display_status(Logs.get_logs())

        last_len = Logs.get_len()


def get_log_line() -> str | None:
    raw_line = sys.stdin.readline()
    log_line = raw_line

    return log_line


def clear_display() -> None:
    os.system("clear")


def display_logs(logs: list[str], screen_buffer_len: int = 50) -> None:
    last_log: str = ""
    counter = 0

    for log in logs[-screen_buffer_len::]:
        if log == last_log and log.strip().lower() not in ["\n", "", "\t"]:
            counter += 1
            continue
        else:
            if counter > 0:
                print(f"\t+{counter} identical")
            counter = 0

        nl = ""
        if log.endswith("\n") and len(log) > Environment.terminal_width:
            nl = "\n"

        print(log[: Environment.terminal_width :], end=nl)

        last_log = log


def display_status(logs: list[str]) -> None:
    print()
    print(f"-= Supalogger captured {len(logs)} logs =-")


def start_display_thread() -> None:
    display_thread = threading.Thread(target=display_thread_worker)
    display_thread.daemon = True
    display_thread.start()


def update_environment() -> None:
    Environment.terminal_width = os.get_terminal_size().columns
    Environment.terminal_height = os.get_terminal_size().lines


def main() -> None:
    start_display_thread()

    while True:
        update_environment()

        log_line = get_log_line()
        Logs.add_entry(log_line)

        ThreadLiveness.check_threads()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by user.")
