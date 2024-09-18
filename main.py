import os
import sys
import threading


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


def log_display_thread() -> None:
    last_len = Logs.get_len()

    while True:
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

        print(log, end="")

        last_log = log


def display_status(logs: list[str]) -> None:
    print()
    print(f"-= Supalogger captured {len(logs)} logs =-")


def start_display_thread() -> None:
    display_thread = threading.Thread(target=log_display_thread)
    display_thread.daemon = True
    display_thread.start()


def main() -> None:
    start_display_thread()

    while True:
        log_line = get_log_line()
        Logs.add_entry(log_line)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by user.")
