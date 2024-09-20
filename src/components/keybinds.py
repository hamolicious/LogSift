from textual.app import ComposeResult
from textual.widgets import Label
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.containers import Grid
import string


class KeybindsInfo(ModalScreen):
    DEFAULT_CSS = """
        KeybindsInfo {
            align: center middle;
        }

        #keybinds-panel {
            padding: 1;
            layout: grid;
            width: 75%;
            height: 75%;
            background: $panel;
            grid-size: 5 15;
        }

        .keybind-info-card {
            border-top: thick $primary;
            padding: 1;
            padding-top: 0;
            width: 90%;
            height: 90%;
            background: $panel-lighten-1;
            row-span: 3;
            column-span: 1;
        }

        #title {
            background: $primary;
            color: $text;
            padding-left: 1;
            width: 15%;
            height: 1;
            row-span: 3;
            column-span: 1;
        }
    """

    BINDINGS = [
        Binding("escape", "dismiss", "close self"),
    ]

    def __init__(
        self,
        bindings: tuple[Binding, ...],
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self.source_bindings = self.sorted(bindings)

    def sorted(self, bindings: tuple[Binding, ...]) -> tuple[Binding, ...]:
        return tuple(sorted(bindings, key=lambda bind: bind.key))

    def build_card(self, binding: Binding) -> Label:
        key = binding.key
        char = ",".join(
            [
                f"shift+{k.lower()}" if k in string.ascii_uppercase else k
                for k in key.split(",")
            ]
        )
        char_line = ",".join(
            [f"[bold underline]{k}[/bold underline]" for k in char.split(",")]
        )

        return Label(
            f"{char_line}\n{binding.description}",
            classes="keybind-info-card",
        )

    def compose(self) -> ComposeResult:
        yield Label("Key Bindings", id="title")
        with Grid(id="keybinds-panel"):

            for binding in self.source_bindings:
                yield self.build_card(binding)
