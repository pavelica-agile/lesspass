import sys

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Label, Static, Switch

from lesspass import exceptions
from lesspass.clipboard import copy, get_system_copy_command
from lesspass.password import generate_password


class LessPassTui(App):
    TITLE = "LessPass"
    SUB_TITLE = "Stateless password generator"
    CSS = """
    Screen {
        align: center middle;
    }

    #main {
        width: 72;
        max-width: 95%;
        height: auto;
        padding: 1 2;
        border: round $accent;
        background: $surface;
    }

    .field-row {
        height: 3;
        margin: 0;
    }

    .field-row Label {
        width: 16;
        padding: 1 0;
    }

    .options {
        height: 3;
        margin: 0;
    }

    .options Label {
        width: auto;
        padding: 1 1 1 0;
    }

    #password {
        height: 3;
        margin: 1 0;
        padding: 1 2;
        border: round $success;
        color: $text;
        text-style: bold;
    }

    #status {
        height: 2;
        color: $text-muted;
    }

    #status.error {
        color: $error;
    }

    #generate {
        width: 1fr;
    }

    #copy {
        width: 1fr;
    }
    """

    BINDINGS = [
        ("ctrl+g", "generate", "Generate"),
        ("ctrl+c", "copy_password", "Copy"),
        ("ctrl+q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="main"):
            with Horizontal(classes="field-row"):
                yield Label("Site")
                yield Input(placeholder="example.org", id="site")
            with Horizontal(classes="field-row"):
                yield Label("Login")
                yield Input(placeholder="name@example.org", id="login")
            with Horizontal(classes="field-row"):
                yield Label("Master password")
                yield Input(password=True, id="master-password")
            with Horizontal(classes="field-row"):
                yield Label("Length")
                yield Input(value="16", type="integer", id="length")
            with Horizontal(classes="field-row"):
                yield Label("Counter")
                yield Input(value="1", type="integer", id="counter")
            with Horizontal(classes="options"):
                yield Label("Character sets")
                yield Label("a-z")
                yield Switch(value=True, id="lowercase")
                yield Label("A-Z")
                yield Switch(value=True, id="uppercase")
                yield Label("0-9")
                yield Switch(value=True, id="digits")
                yield Label("symbols")
                yield Switch(value=True, id="symbols")
            with Horizontal(classes="field-row"):
                yield Label("Exclude")
                yield Input(placeholder="characters to omit", id="exclude")
            yield Static(
                "Your generated password will appear here",
                id="password",
                markup=False,
            )
            yield Static("", id="status")
            with Horizontal():
                yield Button("Generate", id="generate", variant="primary")
                yield Button("Copy", id="copy", disabled=True)
                yield Button("Reveal master", id="reveal")
        yield Footer()

    def on_mount(self) -> None:
        self._generated_password = ""
        self.query_one("#site", Input).focus()

    def _value(self, widget_id: str) -> str:
        return self.query_one(f"#{widget_id}", Input).value.strip()

    def _set_status(self, message: str, error: bool = False) -> None:
        status = self.query_one("#status", Static)
        status.update(message)
        status.set_class(error, "error")

    def action_generate(self) -> None:
        self._generate()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "generate":
            self._generate()
        elif event.button.id == "copy":
            self.action_copy_password()
        elif event.button.id == "reveal":
            master_password = self.query_one("#master-password", Input)
            master_password.password = not master_password.password
            event.button.label = "Hide master" if not master_password.password else "Reveal master"

    def _generate(self) -> None:
        site = self._value("site")
        master_password = self.query_one("#master-password", Input).value
        if not site or not master_password:
            self._set_status("Site and master password are required.", error=True)
            return

        try:
            length = int(self._value("length"))
            counter = int(self._value("counter"))
            if not 5 <= length <= 35:
                raise ValueError("length must be between 5 and 35")
            if counter < 1:
                raise ValueError("counter must be at least 1")
            profile = {
                "site": site,
                "login": self._value("login"),
                "length": length,
                "counter": counter,
                "exclude": self._value("exclude"),
                "lowercase": self.query_one("#lowercase", Switch).value,
                "uppercase": self.query_one("#uppercase", Switch).value,
                "digits": self.query_one("#digits", Switch).value,
                "symbols": self.query_one("#symbols", Switch).value,
            }
            generated_password = generate_password(profile, master_password)
        except ValueError as error:
            self._set_status(str(error), error=True)
            return
        except exceptions.ExcludeAllCharsAvailable:
            self._set_status("The excluded characters remove every available character.", error=True)
            return

        self._generated_password = generated_password
        self.query_one("#password", Static).update(generated_password)
        self.query_one("#copy", Button).disabled = False
        self._set_status("Password generated.")

    def action_copy_password(self) -> None:
        password = self._generated_password
        if not password:
            self._set_status("Generate a password first.", error=True)
            return
        if not get_system_copy_command():
            self._set_status("No supported clipboard command is available.", error=True)
            return
        try:
            copy(password)
        except Exception:
            self._set_status("Copy failed.", error=True)
        else:
            self._set_status("Password copied to the clipboard.")


def main() -> None:
    LessPassTui().run()


if __name__ == "__main__":
    sys.exit(main())