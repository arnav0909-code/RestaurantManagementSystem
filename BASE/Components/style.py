import tkinter as tk
from tkinter import ttk, font as tkfont

ACCENT = "#b45309"
ACCENT_HOVER = "#92400e"
ACCENT_MUTED = "#f5efe6"
BG = "#fafaf9"
SURFACE = "#ffffff"
FG = "#1c1917"
MUTED = "#78716c"
BORDER = "#e7e5e4"

_PREFERRED = ("Helvetica Neue", "Helvetica", "Arial", "TkDefaultFont")


def pick_family():
    available = set(tkfont.families())
    for family in _PREFERRED:
        if family in available:
            return family
    return "TkDefaultFont"


def apply_theme(root):
    family = pick_family()
    body = (family, 11)
    style = ttk.Style(root)

    if "clam" in style.theme_names():
        style.theme_use("clam")

    root.option_add("*TCombobox*Listbox.background", SURFACE)
    root.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
    root.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")

    style.configure(".", font=body, background=BG, foreground=FG)
    style.configure("TFrame", background=BG)
    style.configure("TLabel", background=BG, foreground=FG, font=body)
    style.configure("Title.TLabel", font=(family, 20, "bold"))
    style.configure("Heading.TLabel", font=(family, 14, "bold"))
    style.configure("Sub.TLabel", font=body, foreground=MUTED)
    style.configure("Muted.TLabel", font=(family, 9), foreground=MUTED)
    style.configure("Accent.TLabel", font=(family, 13, "bold"), foreground=ACCENT)

    style.configure(
        "TButton",
        font=body,
        padding=(12, 7),
        relief="flat",
        borderwidth=1,
        bordercolor=BORDER,
        background=SURFACE,
        foreground=FG,
    )
    style.map(
        "TButton",
        background=[("active", ACCENT_MUTED), ("disabled", BG)],
        foreground=[("disabled", "#c8c5c2")],
        bordercolor=[("active", ACCENT)],
    )
    style.configure(
        "Accent.TButton",
        background=ACCENT,
        foreground="#ffffff",
        bordercolor=ACCENT,
        font=(family, 11, "bold"),
    )
    style.map(
        "Accent.TButton",
        background=[("active", ACCENT_HOVER), ("disabled", BORDER)],
        foreground=[("active", "#ffffff"), ("disabled", "#f0efed")],
        bordercolor=[("active", ACCENT_HOVER), ("disabled", BORDER)],
    )
    style.configure("Ghost.TButton", background=BG, bordercolor=BG)
    style.map(
        "Ghost.TButton",
        background=[("active", ACCENT_MUTED)],
        bordercolor=[("active", BORDER)],
    )

    style.configure(
        "TEntry",
        fieldbackground=SURFACE,
        foreground=FG,
        bordercolor=BORDER,
        lightcolor=BORDER,
        darkcolor=BORDER,
        insertcolor=FG,
        padding=(6, 5),
    )
    style.map("TEntry", bordercolor=[("focus", ACCENT)], lightcolor=[("focus", ACCENT)])
    style.configure(
        "TSpinbox",
        fieldbackground=SURFACE,
        foreground=FG,
        bordercolor=BORDER,
        arrowcolor=FG,
        padding=(6, 5),
    )
    style.configure("TMenubutton", font=body, padding=(12, 6), background=SURFACE)
    style.map(
        "TMenubutton",
        background=[("active", ACCENT_MUTED)],
        bordercolor=[("active", ACCENT)],
    )
    style.configure(
        "MenuBar.TMenubutton",
        font=body,
        padding=(9, 3),
        background=BG,
        borderwidth=0,
        relief="flat",
    )
    style.map(
        "MenuBar.TMenubutton",
        background=[("active", ACCENT_MUTED)],
        bordercolor=[("active", BORDER)],
    )
    style.layout(
        "MenuBar.TMenubutton",
        [
            (
                "Menubutton.border",
                {
                    "sticky": "nswe",
                    "children": [
                        (
                            "Menubutton.padding",
                            {
                                "sticky": "we",
                                "children": [
                                    ("Menubutton.label", {"side": "left", "sticky": ""})
                                ],
                            },
                        )
                    ],
                },
            )
        ],
    )

    style.configure("TLabelframe", background=BG, bordercolor=BORDER, relief="solid")
    style.configure(
        "TLabelframe.Label", background=BG, foreground=ACCENT, font=(family, 10, "bold")
    )

    style.configure(
        "Treeview",
        background=SURFACE,
        fieldbackground=SURFACE,
        foreground=FG,
        rowheight=28,
        bordercolor=BORDER,
        borderwidth=1,
    )
    style.configure(
        "Treeview.Heading",
        font=(family, 10, "bold"),
        background=ACCENT_MUTED,
        foreground=ACCENT,
        borderwidth=0,
        relief="flat",
        padding=(6, 7),
    )
    style.map("Treeview.Heading", background=[("active", BORDER)])
    style.map(
        "Treeview",
        background=[("selected", ACCENT)],
        foreground=[("selected", "#ffffff")],
    )

    style.configure("TNotebook.Tab", font=body, padding=(14, 7))
    style.map("TNotebook.Tab", foreground=[("selected", ACCENT)])
    style.configure("TNotebook", bordercolor=BORDER, background=BG)

    style.configure(
        "TScrollbar",
        background=BORDER,
        troughcolor=BG,
        bordercolor=BG,
        arrowcolor=MUTED,
        borderwidth=0,
    )
    return style
