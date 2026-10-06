import os
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image

from Database import Database


class ProductSelector(tk.Frame):
    def __init__(self, parent, root_frame, row, func):
        self.func = func
        tk.Frame.__init__(self, parent)

        self.init_database()

        self.menuBtn = ttk.Menubutton(root_frame, text="Select a meal", width=14)

        self.menu = tk.Menu(self.menuBtn, tearoff=0)
        self.m_var1 = tk.StringVar()
        self.m_var1.set("Select a meal")
        self.retrieve_products()
        self.menuBtn['menu'] = self.menu
        # Rebuild the list before the menu is posted. FocusIn and Button-1
        # fire in different orders depending on the platform, so bind both;
        # refresh_products is idempotent.
        self.menuBtn.bind("<FocusIn>", self.refresh_products)
        self.menuBtn.bind("<Button-1>", self.refresh_products)

        self.menuBtn.grid(column=0, row=row, padx=(12, 24), sticky=tk.W)

        self.pr_qty_var = tk.StringVar(root_frame)
        self.pr_qty_var.set("1")
        self.spin_box = ttk.Spinbox(
            root_frame,
            from_=1,
            to=100,
            textvariable=self.pr_qty_var,
            wrap=True,
            width=5,
            state=tk.DISABLED,
        )
        self.spin_box.grid(column=1, row=row)

        self.order_st_lb = ttk.Label(root_frame,  text="Choosing", style="Muted.TLabel")
        self.order_st_lb.grid(column=2, row=row, padx=(30, 10), sticky=tk.W)

        self.del_icon_png = Image.open(
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'delete.png'))
        self.del_icon_res = self.del_icon_png.resize(
            (18, 18), Image.Resampling.LANCZOS)
        self.del_icon = ImageTk.PhotoImage(self.del_icon_res)
        self.destroy_btn = ttk.Button(
            root_frame, image=self.del_icon, width=3, command=self.destroy_all)
        self.destroy_btn.image = self.del_icon
        self.destroy_btn.grid(column=3, row=row, padx=(10, 0))

    def init_database(self):
        self.fac_db = Database("restaurant.db")
        self.fac_db.ensure_menu_config()

    def retrieve_products(self):
        for name in self.available_product_names():
            self.menu.add_radiobutton(
                label=name, variable=self.m_var1, command=self.sel)

    def available_product_names(self):
        load_query = """SELECT product_name FROM menu_config
            WHERE available = 1 ORDER BY id"""
        return [row[0] for row in self.fac_db.read_val(load_query)]

    def refresh_products(self, event=None):
        """Rebuild the dropdown so a dish marked sold out elsewhere
        disappears without the cashier restarting the order screen."""
        try:
            names = self.available_product_names()
            self.menu.delete(0, tk.END)
            for name in names:
                self.menu.add_radiobutton(
                    label=name, variable=self.m_var1, command=self.sel)
            if self.m_var1.get() not in names:
                self.reset_selection()
        except tk.TclError:
            pass

    def reset_selection(self):
        self.m_var1.set("Select a meal")
        self.menuBtn.config(text="Select a meal")
        self.order_st_lb.config(text="Choosing")
        self.spin_box.config(state=tk.DISABLED)

    def sel(self):
        selx = self.m_var1.get()
        self.menuBtn.config(text=selx)
        self.order_updt()

    def retrieve_data(self):
        return (self.m_var1.get(), self.pr_qty_var.get())

    def order_updt(self):
        self.order_st_lb.config(text="Ordered")
        self.spin_box.config(state=tk.ACTIVE)
        self.spin_box.config(textvariable=self.pr_qty_var)

    def destroy_all(self):
        super().destroy()
        self.menuBtn.destroy()
        self.menu.destroy()
        self.spin_box.destroy()
        self.order_st_lb.destroy()
        self.destroy_btn.destroy()
        func = getattr(self, "func", None)
        if func is None:
            return
        try:
            func()
        except tk.TclError:
            pass
