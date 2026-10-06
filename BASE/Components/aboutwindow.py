import tkinter as tk
from tkinter import ttk

from style import apply_theme, pick_family, MUTED, BG, FG, ACCENT


class AboutWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        apply_theme(self)
        self.configure(background=BG)

        self.win_width = 400
        self.win_height = 300
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        self.center_x = int(screen_width/2 - self.win_width/2)
        self.center_y = int(screen_height/2 - self.win_height/2)

        self.geometry(
            f'{self.win_width}x{self.win_height}+{self.center_x}+{self.center_y}')
        self.resizable(0, 0)
        self.title('About the application')

        outer = ttk.Frame(self, padding=(28, 24))
        outer.pack(fill=tk.BOTH, expand=True)

        heading = ttk.Label(
            outer, text="Restaurant Management System", style="Heading.TLabel")
        heading.pack(anchor=tk.W)

        sub = ttk.Label(
            outer, text="Version 0.1.2  ·  developed by Arnav Argulwar", style="Muted.TLabel")
        sub.pack(anchor=tk.W, pady=(2, 16))

        rule = tk.Frame(outer, height=2, background=ACCENT)
        rule.pack(fill=tk.X, pady=(0, 16))

        about_lbl = ttk.Label(
            outer,
            wraplength=330,
            justify='left',
            text="This application is developed by Arnav Argulwar as a mini project for the "
                 "Programming course of Bca."
                 "It manages a restaurant's configuration, menu and tables, "
                 "takes orders from customers, passes them to the kitchen, and produces "
                 "bills once orders are fulfilled. Development started September 2026."
        )
        about_lbl.pack(anchor=tk.W)
