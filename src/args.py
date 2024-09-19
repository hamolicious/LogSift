import sys


def get_args() -> str | None:
    if len(sys.argv) < 1:
        return None

    command = " ".join(sys.argv[1::])

    return command
