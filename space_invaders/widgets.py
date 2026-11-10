"""Building blocks shared by every screen in the main window."""
from tkinter import ttk

from . import theme


class Screen(ttk.Frame):
    """One page of the main window, e.g. the login form or the menu.

    Subclasses add their widgets to self.body in build(), which is kept in the middle of
    the window, and can give focus to a box in on_show().
    """

    def __init__(self, parent, app, **options):
        super().__init__(parent, padding=theme.px(theme.PADDING))
        self.app = app
        self.options = options
        self.message = None
        self.body = ttk.Frame(self)
        self.body.pack(expand=True, fill="x")  # expand without filling vertically = centred
        self.build()

    def build(self):
        """Create the screen's widgets."""

    def on_show(self):
        """Called after the screen is displayed."""

    # --- Helpers for laying out a screen top to bottom ------------------------------

    def add_title(self, text, subtitle=None):
        ttk.Label(self.body, text=text, style="Title.TLabel").pack(pady=(0, theme.px(4)))
        if subtitle:
            ttk.Label(self.body, text=subtitle, style="Muted.TLabel").pack(pady=(0, theme.px(theme.GAP)))

    def add_heading(self, text):
        ttk.Label(self.body, text=text, style="Heading.TLabel").pack(pady=(0, theme.px(theme.GAP)))

    def add_field(self, label, hidden=False):
        """Add a label and a text box underneath it. Returns the text box."""
        ttk.Label(self.body, text=label, style="Muted.TLabel").pack(
            fill="x", pady=(theme.px(theme.FIELD_GAP), 0))
        entry = ttk.Entry(self.body, show="•" if hidden else "")
        entry.pack(fill="x", pady=theme.px(theme.FIELD_GAP))
        return entry

    def add_button(self, text, command, primary=False):
        style = "Accent.TButton" if primary else "TButton"
        button = ttk.Button(self.body, text=text, command=command, style=style)
        button.pack(fill="x", pady=(theme.px(theme.GAP // 2), 0))
        return button

    def add_message_line(self):
        """Add the line under a form where errors and confirmations appear."""
        self.message = ttk.Label(self.body, text="", style="Error.TLabel",
                                 wraplength=theme.px(theme.TEXT_WIDTH), justify="center")
        self.message.pack(pady=(theme.px(theme.GAP // 2), 0))
        initial = self.options.get("message")
        if initial:
            self.show_success(initial)
        return self.message

    def add_back_button(self, command, text="← Back"):
        ttk.Button(self.body, text=text, command=command, style="Link.TButton").pack(
            pady=(theme.px(theme.GAP), 0))

    # --- Messages ------------------------------------------------------------------

    def show_error(self, text):
        self.message.configure(text=text, style="Error.TLabel")

    def show_success(self, text):
        self.message.configure(text=text, style="Success.TLabel")

    def clear_message(self):
        if self.message is not None:
            self.message.configure(text="")
