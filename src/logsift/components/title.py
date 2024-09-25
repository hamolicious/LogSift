from typing import Literal, TypeAlias
from textual.app import ComposeResult
from textual.widgets import Static, Label
from textual.containers import Center

Variants: TypeAlias = Literal["h1", "h2"]


class Title(Static):

    DEFAULT_CSS = """
        .title-container {
            width: 100%;
            height: 2;
            margin: 0;
            padding: 0;
        }

        .padding-top {
            padding-top: 1;
        }

        .title {
            text-style: bold;
        }

        .title-h1 {
            color: $secondary;
            text-style: bold underline;
        }

        .title-h2 {
            padding-top: 1;
            color: $text;
        }
    """

    def __init__(
        self,
        text="",
        *,
        variant: Variants = "h2",
        padding: bool = True,
        expand=False,
        shrink=False,
        markup=True,
        name=None,
        id=None,
        classes=None,
        disabled=False,
    ):
        super().__init__(
            text,
            expand=expand,
            shrink=shrink,
            markup=markup,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

        self.variant: Variants = variant
        self.padding = padding

    def compose(self) -> ComposeResult:
        classes = "title" + (" padding-top" if self.padding else "")

        match self.variant:
            case "h1":
                with Center(classes="title-container"):
                    yield Label(self.renderable, classes=f"{classes} title-h1")

            case "h2":
                yield Label(self.renderable, classes=f"{classes} title-h2")
