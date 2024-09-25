from textual.app import ComposeResult
from textual.widgets import MarkdownViewer, Label, Static
from textual.containers import Container
from textual.binding import Binding


class Documentation(Static):
    DEFAULT_CSS = """
        Documentation {
            align: center middle;
        }

        #body {
            padding: 1;
            background: $panel;
        }
    """

    BINDINGS = [
        Binding("escape", "dismiss", "close self"),
    ]

    def __init__(self, docs: str, id: str = "", classes: str = "") -> None:
        super().__init__(id=id, classes=classes)

        self.docs = docs

    def compose(self) -> ComposeResult:
        yield Label("Documentation", id="title")
        with Container(id="body"):
            yield MarkdownViewer(self.docs, show_table_of_contents=True)
