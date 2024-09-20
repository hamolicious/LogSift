from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import MarkdownViewer, Label
from textual.containers import Container
from textual.binding import Binding


class Documentation(ModalScreen):
    DEFAULT_CSS = """
        Documentation {
            align: center middle;
        }

        #body {
            padding: 1;
            width: 80%;
            height: 80%;
            background: $panel;
        }

        #title {
            background: $primary;
            color: $text;
            padding-left: 1;
            width: 15%;
            height: 1;
        }

        MarkdownViewer {
        }
    """

    BINDINGS = [
        Binding("escape", "dismiss", "close self"),
    ]

    def __init__(self) -> None:
        super().__init__()

    def load_docs(self) -> str:
        with open("docs/Introduction.md", "r") as f:
            return f.read()

    def compose(self) -> ComposeResult:
        yield Label("Documentation", id="title")
        with Container(id="body"):
            yield MarkdownViewer(self.load_docs(), show_table_of_contents=True)
