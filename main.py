import os
import time
import sys


def get_log_line() -> str | None:
    raw_line = sys.stdin.readline()
    log_line = raw_line

    return log_line


def clear_display() -> None:
    os.system('clear')


def display_logs(logs: list[str], screen_buffer_len: int = 50) -> None:
    last_log: str = ''
    counter = 0

    for log in logs[-screen_buffer_len::]:
        if log == last_log and log.strip().lower() not in ['\n', '', '\t']:
            counter += 1
            continue
        else:
            if counter > 0:
                print(f'\t+{counter} identical')
            counter = 0

        print(log, end='')

        last_log = log


def display_status(logs: list[str]) -> None:
    print()
    print(f'-= Supalogger captured {len(logs)} logs =-')


def main() -> None:
    logs: list[str] = []

    while True:
        log_line = get_log_line()
        if not log_line:
            continue

        logs.append(log_line)

        clear_display()
        display_logs(logs)
        display_status(logs)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped by user.")


