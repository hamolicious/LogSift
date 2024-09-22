from textual.binding import Binding
from src.types.ids import Ids

BINDINGS: tuple[Binding, ...] = (
    Binding(
        "L",
        action="log",
        description="Logs a value to the logger (development only)",
    ),
    Binding(
        "f",
        action=f"focus('#{Ids.FILTER}')",
        description="Focuses the filter input",
    ),
    Binding(
        "p",
        action=f"toggle_setting('#{Ids.PAUSE_INGESTING_LOGS_TOGGLE}')",
        description="Pause listing of logs",
    ),
    Binding(
        "t",
        action=f"toggle_setting('#{Ids.FILTER_TOGGLE}')",
        description="Toggle enforcing the filter",
    ),
    Binding(
        "m",
        action=f"toggle_setting('#{Ids.MATCH_ALL}')",
        description="Toggle between matching either all or at least 1 term from filter",
    ),
    Binding(
        "c",
        action=f"toggle_setting('#{Ids.CASE_INSENSITIVE_TOGGLE}')",
        description="Toggle case sensitivity/insensitivity",
    ),
    Binding(
        "o",
        action=f"toggle_setting('#{Ids.FILTER_OMIT}')",
        description="Omit non-matching logs",
    ),
    Binding(
        "l",
        action=f"toggle_setting('#{Ids.FILTER_HIGHLIGHT}')",
        description="Highlight matching logs",
    ),
    Binding(
        "b",
        action=f"toggle_visible('#{Ids.SETTINGS_CONTAINER}')",
        description="Toggle settings panel visibility",
    ),
    Binding(
        "H",
        action=f"toggle_visible('#{Ids.DOCUMENTATION_CONTAINER}')",
        description="Toggle docs panel visibility",
    ),
    Binding(
        "j,down",
        action="scroll_logger('down')",
        description="Scroll logger down",
    ),
    Binding(
        "k,up",
        action="scroll_logger('up')",
        description="Scroll logger up",
    ),
    Binding(
        "J",
        action="scroll_logger('fdown')",
        description="Scroll logger 10 lines down",
    ),
    Binding(
        "K",
        action="scroll_logger('fup')",
        description="Scroll logger 10 lines up",
    ),
    Binding(
        "C",
        action="copy_shown",
        description="Copy filtered logs to clipboard",
    ),
)
