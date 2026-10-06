import os
import traceback
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import ImageTk, Image
from sqlite3 import Error

from printorders import PrintOrders
from configwindow import ConfigWindow
from kitchenwindow import KitchenWindow
from createorders import CreateOrders
from aboutwindow import AboutWindow
from Database import Database
from style import apply_theme, pick_family, ACCENT, ACCENT_MUTED, MUTED, BG, FG

# basedir = os.path.dirname(__file__)
# print(basedir)


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        apply_theme(self)
        self.configure(background=BG)

        self.win_width = 600
        self.win_height = 420
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        self.center_x = int(screen_width/2 - self.win_width/2)
        self.center_y = int(screen_height/2 - self.win_height/2)

        self.geometry(
            f'{self.win_width}x{self.win_height}+{self.center_x}+{self.center_y}')
        self.resizable(0, 0)
        self.title('Restaurant Management System')

        self.m_frame = ttk.Frame(self, width=600, height=400)
        self.m_frame.grid(row=0, column=0,  sticky=tk.NSEW)
        self.m_frame.columnconfigure(0, weight=1)

        icon_path = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'assets', 'icon_m.png')
        self.icon_image = Image.open(icon_path)
        self.python_image = ImageTk.PhotoImage(self.icon_image)

        self.iconphoto(True, self.python_image)

        self.menubar = tk.Menu(self.m_frame)
        self.filebar = tk.Menu(self.menubar, tearoff=0)
        self.filebar.add_cascade(
            label="Print Receipts", command=self.print_win, state=tk.DISABLED)
        self.filebar.add_cascade(
            label="Kitchen", command=self.kitchen_win, state=tk.DISABLED)
        self.filebar.add_cascade(
            label="Create Orders", command=self.customer_win, state=tk.DISABLED)
        self.filebar.add_cascade(
            label="Configure Facility/Menu", command=self.config_window)
        self.filebar.add_separator()
        self.filebar.add_cascade(label="Exit", command=self.quit)
        self.menubar.add_cascade(label="File", menu=self.filebar)

        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label="About...", command=self.about_win)
        self.menubar.add_cascade(label="About", menu=self.helpmenu)

        self.config(menu=self.menubar)

        self.bar_frame = ttk.Frame(self.m_frame, relief=tk.GROOVE, borderwidth=1)
        self.bar_frame.grid(row=0, column=0, sticky=tk.EW)

        self.file_btn = ttk.Menubutton(
            self.bar_frame, text="File", width=7, style="MenuBar.TMenubutton")
        self.file_btn.grid(row=0, column=0, sticky=tk.W, padx=(6, 2), pady=3)
        self.file_btn["menu"] = self.filebar

        self.about_btn = ttk.Menubutton(
            self.bar_frame, text="About", width=7, style="MenuBar.TMenubutton")
        self.about_btn.grid(row=0, column=1, sticky=tk.W, padx=(2, 6), pady=3)
        self.about_btn["menu"] = self.helpmenu

        self.img = Image.open(os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 'assets', 'main_win_ph.png'))
        self.img = self.img.resize((200, 200), Image.Resampling.LANCZOS)
        self.img = ImageTk.PhotoImage(self.img)
        self.panel = tk.Label(
            self.m_frame,
            image=self.img,
            text="Restaurant Management System",
            compound='top',
            background=BG,
            foreground=FG,
            font=(pick_family(), 19, "bold"),
            pady=8,
        )
        self.panel.image = self.img
        self.panel.grid(row=1, column=0, sticky=tk.NSEW, padx=88, pady=(24, 10))

        self.tagline = tk.Label(
            self.m_frame,
            text="Orders, kitchen and billing in one place",
            background=BG,
            foreground=MUTED,
            font=(pick_family(), 10),
        )
        self.tagline.grid(row=2, column=0, sticky=tk.N, pady=(0, 14))

        self.vers = tk.Label(
            self.m_frame,
            text="v0.1.2, N.A",
            background=BG,
            foreground=MUTED,
            font=(pick_family(), 9),
        )
        self.vers.grid(row=3, column=0, sticky=tk.SW, padx=12, pady=(0, 8))
        self.check_databases()

    def check_databases(self):
        try:
            self.fac_db = Database("restaurant.db")
            load_query = """SELECT * FROM menu_config"""
            res = self.fac_db.read_val(load_query)
            customer_state = tk.NORMAL if res else tk.DISABLED
            self.filebar.entryconfig(2, state=customer_state)

            load_query1 = """SELECT * FROM orders"""
            res1 = self.fac_db.read_val(load_query1)

            kitchen_state = tk.NORMAL if res1 else tk.DISABLED
            self.filebar.entryconfig(1, state=kitchen_state)

            load_query2 = """SELECT * FROM cooked_orders"""
            res2 = self.fac_db.read_val(load_query2)

            print_order_state = tk.NORMAL if res2 else tk.DISABLED
            self.filebar.entryconfig(0, state=print_order_state)
        except Error as e:
            print(e)
        except tk.TclError:
            pass

    def _raise_window(self, win):
        try:
            win.deiconify()
            win.lift()
            win.focus_force()
        except tk.TclError:
            pass

    def _grab_window(self, win):
        try:
            win.grab_set()
        except tk.TclError:
            pass

    def _refresh_window(self, win):
        refresh = getattr(win, "refresh_facility_info", None)
        if refresh is None:
            return
        try:
            refresh()
        except (tk.TclError, IndexError, TypeError):
            pass

    def show_window(self, cls, *args):
        for w in self.winfo_children():
            if not isinstance(w, cls):
                continue
            try:
                alive = w.winfo_exists()
            except tk.TclError:
                alive = False
            if alive:
                self._raise_window(w)
                self._refresh_window(w)
                return w
            try:
                w.destroy()
            except tk.TclError:
                pass

        try:
            win = cls(self, *args)
        except Exception:
            for w in self.winfo_children():
                if isinstance(w, cls):
                    try:
                        w.destroy()
                    except tk.TclError:
                        pass
            messagebox.showerror(
                "Restaurant Management System",
                f"{cls.__name__} could not be opened.\n\n{traceback.format_exc()}")
            return None

        win.transient(self)
        try:
            win.update_idletasks()
        except tk.TclError:
            pass
        win.after(1, self._present_window, win)
        return win

    def _present_window(self, win):
        try:
            win.wait_visibility()
        except tk.TclError:
            pass
        try:
            win.update_idletasks()
        except tk.TclError:
            pass
        self._raise_window(win)
        self._refresh_window(win)
        self._grab_window(win)

    def config_window(self):
        return self.show_window(ConfigWindow, self.check_databases)

    def kitchen_win(self):
        return self.show_window(KitchenWindow, self.check_databases)

    def customer_win(self):
        return self.show_window(CreateOrders, self.check_databases)

    def about_win(self):
        return self.show_window(AboutWindow)

    def print_win(self):
        return self.show_window(PrintOrders)
