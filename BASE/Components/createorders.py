import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from sqlite3 import Error

from Database import Database
from productselector import ProductSelector
from style import apply_theme, BG, SURFACE


class CreateOrders(tk.Toplevel):
    def __init__(self, parent, func):
        super().__init__(parent)
        apply_theme(self)
        self.configure(background=BG)
        self.func = func
        self.init_database()

        self.order_ls = []

        self.win_width = 600
        self.win_height = 600
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        self.center_x = int(screen_width/2 - self.win_width/2)
        self.center_y = int(screen_height/2 - self.win_height/2)

        self.geometry(
            f'{self.win_width}x{self.win_height}+{self.center_x}+{self.center_y}')
        self.title('Restaurant Management System')
        self.resizable(0, 0)

        # main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(
            row=0,
            column=0,
            sticky=tk.NSEW,
            padx=10,
            pady=10,
            ipady=5,
            ipadx=5
        )

        # Labels
        self.cst_lbl = ttk.LabelFrame(self.main_frame, text="Create Order", padding=12)
        self.cst_lbl.grid(column=0, row=0, columnspan=4,
                          sticky=tk.NSEW, padx=10)

        self.pr_sel_lbl = ttk.Frame(self.cst_lbl)
        self.pr_sel_lbl.grid(column=0, row=5, columnspan=4,
                             rowspan=10, sticky=tk.NSEW)

        self.pr_sel_canvas = tk.Canvas(
            self.pr_sel_lbl, borderwidth=0, width=500, height=360,
            background=SURFACE, highlightthickness=0)
        self.pr_sel_canvas.grid(column=0, row=0, sticky=tk.NSEW)

        self.pr_sel_canvas_frm = ttk.Frame(self.pr_sel_canvas)
        self.cst_lbl_scroller = ttk.Scrollbar(
            self.pr_sel_lbl, command=self.pr_sel_canvas.yview)
        self.cst_lbl_scroller.grid(column=4, row=0, sticky=tk.NS)
        self.pr_sel_canvas.configure(yscrollcommand=self.cst_lbl_scroller.set)

        self.sel_window = self.pr_sel_canvas.create_window(
            (5, 5), anchor=tk.NW, window=self.pr_sel_canvas_frm)

        self.pr_sel_canvas_frm.bind("<Configure>", self.onFrameConfig)
        self.pr_sel_canvas.bind("<Configure>", self.onCanvasConfig)

        self.fac_info = self.retrieve_fac_info()

        self.fc_name = ttk.Label(
            self.cst_lbl, text=self.fac_info[0], style="Accent.TLabel")
        self.fc_name.grid(column=1, row=0)

        self.tb_name = ttk.Label(self.cst_lbl, text="Table number:")
        self.tb_name.grid(column=0, row=1, sticky=tk.W, pady=(8, 0))

        vcmd_tn = (self.register(self.callback_table_num))

        self.tb_name_entry = ttk.Entry(
            self.cst_lbl, width=6, validate='all', validatecommand=(vcmd_tn, "%P"))
        self.tb_name_entry.grid(column=1, row=1, sticky=tk.W, pady=(8, 0))

        self.pr_name = ttk.Label(self.cst_lbl, text="Product Name", style="Muted.TLabel")
        self.pr_name.grid(column=0, row=3, pady=(14, 4))

        self.pr_qty = ttk.Label(self.cst_lbl, text="Quantity", style="Muted.TLabel")
        self.pr_qty.grid(column=1, row=3)

        self.pr_st = ttk.Label(self.cst_lbl, text="Status", style="Muted.TLabel")
        self.pr_st.grid(column=2, row=3)

        self.row_count = tk.IntVar()
        self.row_count.set(1)

        btn_row = ttk.Frame(self.main_frame)
        btn_row.grid(column=0, row=2, columnspan=4, sticky=tk.E, pady=(16, 0))

        self.btn_add_product = ttk.Button(
            btn_row, text="Add product", command=self.add_product)
        self.btn_add_product.grid(column=0, row=0, padx=(0, 8))

        self.close_btn = ttk.Button(
            btn_row, text='Close', command=self.destroy)
        self.close_btn.grid(column=1, row=0, padx=(0, 8))

        self.send_to_ch_btn = ttk.Button(
            btn_row, text='Send to kitchen', style="Accent.TButton",
            state=tk.DISABLED, command=self.send_to_kitchen)
        self.send_to_ch_btn.grid(column=2, row=0)

    def init_database(self):
        self.fac_db = Database("restaurant.db")

        orders_query = """
        CREATE TABLE IF NOT EXISTS orders(
            id integer PRIMARY KEY,
            table_num integer NOT NULL, 
            product_name text NOT NULL,
            order_quantity integer NOT NULL,
            order_status text NOT NULL
        );
        """

        self.fac_db.create_table(orders_query)
        self.fac_db.ensure_menu_config()

    def unavailable_meals(self, orders):
        unavailable = []
        for order in orders:
            meal = order[0][0]
            if meal in unavailable:
                continue
            res = self.fac_db.read_val(
                """SELECT available FROM menu_config WHERE product_name = ?""",
                (meal,))
            if res and not res[0][0]:
                unavailable.append(meal)
        return unavailable

    def retrieve_fac_info(self):
        load_query = """SELECT * FROM fac_config"""
        result = self.fac_db.read_val(load_query)
        if not result:
            return ("", 0)
        fac_name = result[0][1]
        max_table_num = result[0][2]
        return (fac_name, max_table_num)

    def refresh_facility_info(self):
        self.fac_info = self.retrieve_fac_info()
        label = getattr(self, "fc_name", None)
        if label is not None:
            label.config(text=self.fac_info[0])

    def callback_table_num(self, P):
        if (str.isdigit(P) and int(P) <= self.fac_info[1]) or P == "":
            return True
        else:
            messagebox.showerror(
                "Input Error", f"Maximum number of tables must not exceed {self.fac_info[1]}!")
            self.tb_name_entry.delete(0, tk.END)
            return False

    def add_records(self, orders):
        try:
            load_query = """SELECT * FROM orders ORDER BY id DESC LIMIT 1; """
            spec_insert_query = """INSERT INTO orders VALUES (?, ?, ?,  ?, ?)"""
            order_status = "Ordered"
            for order in orders:
                result = self.fac_db.read_val(load_query)
                if result:
                    order_id = result[0][0] + 1
                else:
                    order_id = 1
                order_name = order[0][0]
                order_quantity = int(order[0][1])
                table_num = int(order[1])
                self.fac_db.insert_spec_config(
                    spec_insert_query, (order_id, table_num, order_name, order_quantity, order_status))
        except Error as e:
            print(e)

    def send_to_kitchen(self):
        try:
            orders = []
            table_num = self.tb_name_entry.get()
            if table_num:
                for order in self.order_ls:
                    if order.retrieve_data()[0] == 'Select a meal':
                        messagebox.showerror(
                            "Meal is not selected", "Please, either fill \"Select a meal\" or delete that row to continue!")
                        return False
                    else:
                        orders.append((order.retrieve_data(), table_num))
                unavailable = self.unavailable_meals(orders)
                if unavailable:
                    messagebox.showerror(
                        "Sold out",
                        "The following item(s) have been marked as sold out "
                        "and can no longer be ordered:\n\n"
                        + "\n".join(unavailable))
                    return False
                self.add_records(orders)
                usr_resp = messagebox.askyesno(
                    "Success", "Order have been sent to the kitchen, you can access it through the main window, do you wish to get more orders?")
                if usr_resp:
                    self.clear()
                else:
                    self.destroy()
            else:
                messagebox.showerror(
                    "Empty Fields", "Please enter a valid table number!")
        except Error as e:
            print(e)

    def clear(self):
        self.tb_name_entry.delete(0, tk.END)
        for order in self.order_ls:
            order.destroy_all()
        self.order_ls = []

    def add_product(self):
        self.max = self.pr_sel_canvas_frm.grid_size()
        self.row_count.set((self.row_count.get() + 1)
                           if self.row_count.get() >= self.max[1] else self.max[1] + 1)
        self.pr_sl = ProductSelector(
            self, self.pr_sel_canvas_frm, self.row_count.get(), func=self.des_pr)
        self.order_ls.insert(self.row_count.get(), self.pr_sl)
        self.send_to_ch_btn.config(state=tk.ACTIVE)

    def des_pr(self):
        if len(self.pr_sel_canvas_frm.winfo_children()) == 0:
            self.send_to_ch_btn.config(state=tk.DISABLED)
            self.row_count.set(1)
            self.order_ls = []
        self.set_val = self.row_count.get() - 1 if self.row_count.get() > 1 else 1
        self.row_count.set(self.set_val)

    def onCanvasConfig(self, event):
        self.pr_sel_canvas.itemconfigure(
            self.sel_window, width=max(event.width - 10, 1))
        self.pr_sel_canvas.configure(
            scrollregion=self.pr_sel_canvas.bbox("all"))

    def onFrameConfig(self, event):
        self.pr_sel_canvas.configure(
            scrollregion=self.pr_sel_canvas.bbox("all"))

    def _notify_parent(self):
        func = getattr(self, "func", None)
        if func is None:
            return
        try:
            func()
        except tk.TclError:
            pass

    def destroy(self):
        self._notify_parent()
        super().destroy()

    def __del__(self):
        self._notify_parent()
