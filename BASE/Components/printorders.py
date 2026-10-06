import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from sqlite3 import Error
import os
import webbrowser
import subprocess
from pathlib import Path

from bs4 import BeautifulSoup

from Database import Database
from style import apply_theme, BG, SURFACE

APP_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATE_NAME = "order_template.html"


def template_path():
    path = os.path.join(APP_DIR, TEMPLATE_NAME)
    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"{TEMPLATE_NAME} not found at {path}. It must sit at the "
            "repository root, next to restaurant.db.")
    return path


def set_placeholder(doc, placeholder, value):
    node = doc.find(string=placeholder)
    if node is None:
        for candidate in doc.find_all(string=True):
            if placeholder in candidate:
                node = candidate
                break
    if node is None:
        raise ValueError(
            f'Placeholder "{placeholder}" not found in {TEMPLATE_NAME}. '
            f"It must appear as its own text, e.g. <span>{placeholder}</span>.")
    node.replace_with(value)


class PrintOrders(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        apply_theme(self)
        self.configure(background=BG)
        self.init_database()

        self.order_ls = []

        self.win_width = 640
        self.win_height = 570
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
        self.cst_lbl = ttk.LabelFrame(self.main_frame, text="Print Orders", padding=12)
        self.cst_lbl.grid(column=0, row=0, columnspan=4,
                          sticky=tk.NSEW, padx=10)

        self.fac_info = self.retrieve_fac_info()

        self.fc_name = ttk.Label(
            self.cst_lbl,
            text=self.fac_info[0],
            style="Accent.TLabel"
        )
        self.fc_name.grid(column=1, row=0)

        self.tb_name = ttk.Label(self.cst_lbl, text="Table number:")
        self.tb_name.grid(column=0, row=1, sticky=tk.W, pady=(6, 0))

        vcmd_tn = (self.register(self.callback_table_num))

        self.tb_name_entry = ttk.Entry(
            self.cst_lbl,
            width=6,
            validate='all',
            validatecommand=(vcmd_tn, "%P")
        )
        self.tb_name_entry.grid(row=1, column=1, sticky=tk.W, pady=(6, 0))

        self.tr_v_vscr = ttk.Scrollbar(self.cst_lbl, orient="vertical")

        self.tr_view_columns = ('id', 'name', 'quantity', 'tot_price')
        self.tr_view = ttk.Treeview(
            self.cst_lbl,
            columns=self.tr_view_columns,
            show='headings',
            height=10,
            selectmode='browse',
            yscrollcommand=self.tr_v_vscr.set
        )
        self.tr_view.column('id', width=45, anchor=tk.CENTER)
        self.tr_view.column('name', width=245, anchor=tk.W)
        self.tr_view.column('quantity', width=90, anchor=tk.CENTER)
        self.tr_view.column('tot_price', width=130, anchor=tk.E)

        self.tr_view.heading('id', text="ID")
        self.tr_view.heading('name', text="Product Name")
        self.tr_view.heading('quantity', text="Qty")
        self.tr_view.heading('tot_price', text="Total (Rs)")

        self.tr_view.tag_configure('odd', background=SURFACE)
        self.tr_view.tag_configure('even', background='#f5f5f4')

        self.tr_view.grid(column=0, row=3, rowspan=6,
                          columnspan=3, pady=(14, 0), padx=0)

        self.tr_v_vscr.config(command=self.tr_view.yview)
        self.tr_v_vscr.grid(column=3, row=3, rowspan=6,  sticky=tk.NS, pady=(14, 0))

        self.row_count = tk.IntVar()
        self.row_count.set(1)

        btn_row = ttk.Frame(self.main_frame)
        btn_row.grid(column=0, row=2, columnspan=4, sticky=tk.E, pady=(16, 0))

        self.load_orders_btn = ttk.Button(
            btn_row, text="Load orders", command=self.load_orders)
        self.load_orders_btn.grid(column=0, row=0, padx=(0, 8))

        self.close_btn = ttk.Button(
            btn_row, text='Clear', command=self.clear_all)
        self.close_btn.grid(column=1, row=0, padx=(0, 8))

        self.print_receipt_btn = ttk.Button(
            btn_row,
            text='Print receipt',
            style="Accent.TButton",
            state=tk.DISABLED,
            command=self.print_receipt
        )
        self.print_receipt_btn.grid(column=2, row=0)

    def init_database(self):
        self.fac_db = Database("restaurant.db")
        self.fac_db.ensure_cooked_orders()

    def load_orders(self):
        try:
            self.t_num = self.tb_name_entry.get()
            if self.t_num:
                load_query = """SELECT id, product_name, SUM(order_quantity) as order_quantity, SUM(order_price) as order_price FROM cooked_orders WHERE table_num = ? AND billed = 0  GROUP BY product_name"""
                res = self.fac_db.read_val(load_query, (self.t_num))
                if res:
                    for i, r in enumerate(res):
                        self.tr_view.insert(
                            "", tk.END,
                            tags=('even' if i % 2 else 'odd',),
                            values=(r[0], r[1], r[2], f"{r[3]:.2f}"))
                    self.print_receipt_btn.config(state=tk.ACTIVE)
                else:
                    messagebox.showwarning(
                        "No orders", f"No order has been cooked for table №{self.t_num}")
                    self.print_receipt_btn.config(state=tk.DISABLED)
            else:
                messagebox.showerror(
                    "Empty imput field", "Please fill in the table number to get orders!")
                self.print_receipt_btn.config(state=tk.DISABLED)

        except Error as e:
            print(e)

    def html_row(self, name, quantity, price):
        cells = (name, quantity, price)
        tds = ''.join(
            f"<td class=\"{cls}\">{value}</td>"
            for cls, value in zip(('name', 'qty', 'price'), cells)
        )
        return BeautifulSoup(f"<tr>{tds}</tr>", "html.parser")

    def print_receipt(self):
        rows = []
        tot_p = 0.0
        tot_q = 0
        for child in self.tr_view.get_children():
            val = self.tr_view.item(child)['values']
            tot_p += float(val[3])
            tot_q += int(val[2])
            rows.append(self.html_row(val[1].strip(), val[2], val[3]))

        try:
            with open(template_path(), encoding='utf-8') as html_doc:
                doc = BeautifulSoup(html_doc, 'html.parser')
                set_placeholder(doc, "Fac_name", self.fac_info[0])
                set_placeholder(doc, "t_num", f"Table №{self.t_num}")
                set_placeholder(doc, "summary",
                                f"{tot_q} item{'s' if tot_q != 1 else ''} ordered")
                set_placeholder(doc, "total", f"Total to pay: Rs {tot_p:.2f}")

                tbody = doc.find("tbody", id="items")
                if tbody is None:
                    raise ValueError(
                        f'No <tbody id="items"> found in {TEMPLATE_NAME}; '
                        "the ordered items have nowhere to go.")
                for row in rows:
                    tbody.append(row)

                str_doc = str(doc.prettify())
            receipt_path = os.path.abspath(f"order_{self.t_num}.html")
            with open(receipt_path, "w+", encoding='utf-8') as p_or_fl:
                p_or_fl.write(str_doc)
        except (OSError, ValueError) as e:
            messagebox.showerror("Receipt not created", str(e))
            return

        self.open_receipt(receipt_path)
        self.mark_billed()
        self.clear_all()

    def mark_billed(self):
        try:
            update_query = """
                UPDATE cooked_orders
                SET billed = 1
                WHERE table_num = ? AND billed = 0
                """
            self.fac_db.update(update_query, (self.t_num,))
        except Error as e:
            print(e)

    def open_receipt(self, receipt_path):
        try:
            subprocess.run(['open', receipt_path], check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            webbrowser.open_new_tab(Path(receipt_path).as_uri())

    def clear_all(self):
        self.tb_name_entry.delete(0, tk.END)

        for child in self.tr_view.get_children():
            self.tr_view.delete(child)

        self.print_receipt_btn.config(state=tk.DISABLED)

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

    def destroy(self):
        super().destroy()
