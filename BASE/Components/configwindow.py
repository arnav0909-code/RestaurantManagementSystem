import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from Database import Database
from style import apply_theme, BG


class ConfigWindow(tk.Toplevel):
    def __init__(self, parent, func):
        super().__init__(parent)
        apply_theme(self)
        self.configure(background=BG)
        self.func = func
        self.init_database()

        self.win_width = 520
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        # Clamp to the visible screen so the window can never end up
        # taller than the display (which made it look like it never opened
        # on smaller screens).
        self.win_height = max(400, min(750, screen_height - 60))
        self.i = 5

        self.center_x = int(screen_width/2 - self.win_width/2)
        self.center_y = max(0, int(screen_height/2 - self.win_height/2))

        self.geometry(
            f'{self.win_width}x{self.win_height}+{self.center_x}+{self.center_y}')
        self.title('Restaurant Management System')
        self.minsize(480, 400)
        self.resizable(False, False)
        # Allow the container to expand; inner content scrolls if taller.
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Scrollable container: canvas + scrollbar + inner frame.
        # Previously all widgets were gridded directly in a fixed-size
        # Toplevel with no scroll, so on small screens the content
        # overflowed and the window painted blank/clipped.
        self.canvas = tk.Canvas(
            self, highlightthickness=0, background=BG)
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)
        self.vscroll = ttk.Scrollbar(
            self, orient="vertical", command=self.canvas.yview)
        self.vscroll.grid(row=0, column=1, sticky=tk.NS)
        self.canvas.configure(yscrollcommand=self.vscroll.set)

        # main frame (scrollable body)
        self.main_frame = ttk.Frame(self.canvas)
        self._canvas_win = self.canvas.create_window(
            (0, 0), window=self.main_frame, anchor="nw")
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=0)
        self.main_frame.rowconfigure(1, weight=0)
        self.main_frame.bind(
            "<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self._bind_mousewheel()
        # up frame
        self.up_frame = ttk.Frame(self.main_frame, padding=(10, 10, 10, 0))
        self.up_frame.grid(column=0, row=0, sticky=tk.NSEW)
        self.up_frame.columnconfigure(0, weight=1)

        # down frame
        self.down_frame = ttk.Frame(self.main_frame, padding=(10, 0, 10, 10))
        self.down_frame.grid(column=0, row=1, sticky=tk.NSEW)
        self.down_frame.columnconfigure(0, weight=1)

        # Facility Label frame
        self.fac_config_lf = ttk.LabelFrame(
            self.up_frame, text="Facility Configuration")
        self.fac_config_lf.grid(
            column=0,
            row=0,
            pady=5,
            rowspan=4,
            columnspan=3,
            sticky=tk.EW
        )

        # Labels
        self.fc_name_lb = ttk.Label(self.fac_config_lf, text="Facility Name:")
        self.fc_name_lb.grid(column=0, row=1, sticky=tk.W, padx=10, pady=10)

        # fc_icon_lb = ttk.Label(fac_config_lf, text="Facility Icon")
        # fc_icon_lb.grid(column=0, row=2, sticky=tk.W, padx=15, pady=15)

        self.fc_table_num_lb = ttk.Label(
            self.fac_config_lf,
            text="Number of Tables:"
        )
        self.fc_table_num_lb.grid(
            column=0,
            row=2,
            sticky=tk.W,
            padx=10,
            pady=10
        )

        self.fc_seat_num_lb = ttk.Label(
            self.fac_config_lf,
            text="Number of Seats:"
        )
        self.fc_seat_num_lb.grid(
            column=0,
            row=3,
            sticky=tk.W,
            padx=10,
            pady=10
        )

        # Entries
        self.fc_name_ent = ttk.Entry(self.fac_config_lf)
        self.fc_name_ent.grid(column=1, row=1, sticky=tk.E, padx=15)

        # fc_icon_ent = ttk.Entry(fac_config_lf)
        # fc_icon_ent.grid(column=1, row=2, sticky=tk.E, padx=15)

        vcmd_t = (self.register(self.callback_table))
        vcmd_s = (self.register(self.callback_seats))

        self.fc_table_num_ent = ttk.Entry(
            self.fac_config_lf,
            validate='all',
            validatecommand=(vcmd_t, "%P")
        )
        self.fc_table_num_ent.grid(column=1, row=2, sticky=tk.E, padx=15)

        self.fc_seat_num_ent = ttk.Entry(
            self.fac_config_lf,
            validate='all',
            validatecommand=(vcmd_s, "%P")
        )
        self.fc_seat_num_ent.grid(column=1, row=3, sticky=tk.E, padx=15)

        # buttons
        self.fc_save_btn = ttk.Button(
            self.fac_config_lf, text="Save", command=self.save_fac_config)
        self.fc_save_btn.grid(column=2, row=1, pady=5, padx=15)

        self.fc_load_btn = ttk.Button(
            self.fac_config_lf,
            text="Load",
            command=self.load_fac_config,
            state=tk.DISABLED
        )
        self.fc_load_btn.grid(column=2, row=2, pady=5, padx=15)

        self.fc_clear_btn = ttk.Button(
            self.fac_config_lf,
            text="Clear",
            command=self.fac_conf_clear,
            state=tk.DISABLED
        )
        self.fc_clear_btn.grid(column=2, row=3, pady=5, padx=15)

        # Menu Label Frame
        self.menu_conf_lf = ttk.LabelFrame(
            self.down_frame, text="Menu Configuration")
        # self.menu_conf_lf.config(width=450)
        self.menu_conf_lf.grid(column=0, row=0)

        # TreeView

        self.tr_v_vscr = ttk.Scrollbar(self.menu_conf_lf, orient="vertical")

        self.tr_view_columns = ('id', 'name', 'price', 'status')
        self.tr_view = ttk.Treeview(
            self.menu_conf_lf,
            columns=self.tr_view_columns,
            show='headings',
            height=7,
            selectmode='browse',
            yscrollcommand=self.tr_v_vscr.set
        )
        self.tr_view.column('id', width=50, anchor=tk.CENTER)
        self.tr_view.column('name', width=170, anchor=tk.CENTER)
        self.tr_view.column('price', width=120, anchor=tk.CENTER)
        self.tr_view.column('status', width=110, anchor=tk.CENTER)

        self.tr_view.heading('id', text="ID")
        self.tr_view.heading('name', text="Name")
        self.tr_view.heading('price', text="Price(ft)")
        self.tr_view.heading('status', text="Status")

        self.tr_view.tag_configure('odd', background='#ffffff')
        self.tr_view.tag_configure('even', background='#f5f5f4')
        self.tr_view.tag_configure('sold_out', foreground='#b91c1c')

        self.tr_view.grid(column=0, row=0, rowspan=6, columnspan=4, pady=10)

        self.tr_v_vscr.config(command=self.tr_view.yview)
        self.tr_v_vscr.grid(column=4, row=0, rowspan=6,  sticky=tk.NS)

        self.tr_view.bind('<ButtonRelease-1>', self.product_selected)
        self.tr_view.bind('<Delete>', self.remove_selected)

        # add product labelframe
        self.add_prd_lbf = ttk.LabelFrame(
            self.menu_conf_lf, text="Add product")
        self.add_prd_lbf.grid(column=0, row=7, pady=10,
                              padx=5,  columnspan=3, sticky=tk.EW)

        self.remove_prd_lbf = ttk.LabelFrame(
            self.menu_conf_lf, text="Remove product")
        self.remove_prd_lbf.grid(
            column=0, row=8, pady=10, padx=5,  columnspan=3, sticky=tk.EW)

        # Label and entrys

        self.food_name_lbl = ttk.Label(
            self.add_prd_lbf, text="Name of the product:")
        self.food_name_lbl.grid(column=0, row=0, sticky=tk.W, padx=10, pady=10)

        self.food_price_lbl = ttk.Label(
            self.add_prd_lbf, text="Price of the product:")
        self.food_price_lbl.grid(
            column=0, row=1, sticky=tk.W, padx=10, pady=10)

        self.food_name_entry = ttk.Entry(self.add_prd_lbf)
        self.food_name_entry.grid(column=1, row=0, pady=10, padx=10)

        self.food_price_entry = ttk.Entry(self.add_prd_lbf)
        self.food_price_entry.grid(column=1, row=1, pady=10, padx=10)

        self.pr_id_lbl = ttk.Label(
            self.remove_prd_lbf, text="Product Selected:")
        self.pr_id_lbl.grid(column=0, row=0, sticky=tk.W, padx=10, pady=10)

        self.sel_pr_id_lbl = ttk.Label(self.remove_prd_lbf, text="")
        self.sel_pr_id_lbl.grid(column=1, row=0, sticky=tk.W, padx=10, pady=10)

        # btn tr
        self.tr_view_add = ttk.Button(
            self.add_prd_lbf, text="Add", command=self.add_record)
        self.tr_view_add.grid(column=2, row=0, rowspan=2, padx=10)

        self.tr_view_add.bind('<Return>', self.add_record)

        self.tr_view_remove = ttk.Button(
            self.remove_prd_lbf,
            text="Remove",
            command=self.remove_selected,
            state=tk.DISABLED
        )
        self.tr_view_remove.grid(column=2, row=0, padx=10, sticky=tk.E)

        # availability labelframe
        self.avail_prd_lbf = ttk.LabelFrame(
            self.menu_conf_lf, text="Availability")
        self.avail_prd_lbf.grid(
            column=0, row=9, pady=(10, 0),
            padx=5, columnspan=4, sticky=tk.EW)
        self.avail_prd_lbf.columnconfigure(1, weight=1)

        self.avail_prd_lbl = ttk.Label(
            self.avail_prd_lbf, text="Product Selected:", style="Muted.TLabel")
        self.avail_prd_lbl.grid(column=0, row=0, sticky=tk.W, padx=10, pady=10)

        self.sold_out_btn = ttk.Button(
            self.avail_prd_lbf, text="Mark sold out",
            command=lambda: self.set_product_available(False),
            state=tk.DISABLED)
        self.sold_out_btn.grid(column=2, row=0, padx=(0, 6), pady=8)

        self.available_btn = ttk.Button(
            self.avail_prd_lbf, text="Mark available",
            style="Accent.TButton",
            command=lambda: self.set_product_available(True),
            state=tk.DISABLED)
        self.available_btn.grid(column=3, row=0, padx=(0, 6), pady=8)

        self.restore_all_btn = ttk.Button(
            self.avail_prd_lbf, text="Mark all available",
            command=self.restore_all_products,
            state=tk.DISABLED)
        self.restore_all_btn.grid(column=4, row=0, padx=(0, 6), pady=8)

        self.check_if_empty_database()
        self.check_if_empty_fc_entry()
        self.retreive_menu_items()
        # Force geometry calculation now so the canvas scrollregion is
        # correct before the window is presented (avoids blank first paint
        # on macOS/Aqua).
        try:
            self.update_idletasks()
            self._on_frame_configure()
        except tk.TclError:
            pass

    def _on_frame_configure(self, event=None):
        try:
            self.canvas.configure(
                scrollregion=self.canvas.bbox("all"))
        except tk.TclError:
            pass

    def _on_canvas_configure(self, event=None):
        try:
            width = self.canvas.winfo_width()
            if width > 2:
                self.canvas.itemconfig(self._canvas_win, width=width)
        except tk.TclError:
            pass

    def _on_mousewheel(self, event):
        try:
            if getattr(event, "delta", 0):
                self.canvas.yview_scroll(int(-event.delta / 120), "units")
            elif getattr(event, "num", None) in (4, 5):
                self.canvas.yview_scroll(
                    -1 if event.num == 4 else 1, "units")
        except tk.TclError:
            pass

    def _bind_mousewheel(self):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)
        # Unbind when destroyed so other windows are unaffected.
        self.bind("<Destroy>", lambda e: self._unbind_mousewheel()
                  if e.widget is self else None, add="+")

    def _unbind_mousewheel(self):
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            try:
                self.canvas.unbind_all(seq)
            except tk.TclError:
                pass

    def status_text(self, available):
        return "Available" if available else "Sold out"

    def format_price(self, price):
        try:
            return f"{float(price):.2f}"
        except (TypeError, ValueError):
            return str(price)

    def retreive_menu_items(self, keep_selection=None):
        try:
            load_query = """SELECT id, product_name, product_price, available
                FROM menu_config ORDER BY id"""
            result = self.fac_db.read_val(load_query)
        except Exception as e:
            print(e)
            result = []
        if len(result) > 0:
            for el in result:
                try:
                    sold_out = not el[3]
                    self.tr_view.insert(
                        '', tk.END, iid=f"{el[0]}",
                        tags=('sold_out',) if sold_out else (),
                        values=(el[0], el[1], self.format_price(el[2]),
                                self.status_text(el[3])))
                except Exception as e:
                    # One bad row must never stop the window from opening.
                    print(f"Skipping menu row {el!r}: {e}")
                    continue
            if keep_selection and self.tr_view.exists(f"{keep_selection}"):
                self.tr_view.selection_set(f"{keep_selection}")
                self.tr_view.focus(f"{keep_selection}")
        else:
            self.tr_view_remove.config(state=tk.DISABLED)
        self.sync_availability_buttons()

    def get_product_id(self):
        res = self.tr_view.get_children()
        if res:
            return res[-1]
        else:
            return 1

    def init_database(self):
        self.fac_db = Database("restaurant.db")
        fac_conf_query = """
        CREATE TABLE IF NOT EXISTS fac_config(
            id integer PRIMARY KEY,
            fac_name text NOT NULL,
            table_num integer NOT NULL,
            seat_num integer NOT NULL
        );
        """

        menu_conf_query = """
        CREATE TABLE IF NOT EXISTS menu_config(
            id integer PRIMARY KEY,
            product_name text NOT NULL,
            product_price real NOT NULL,
            available integer NOT NULL DEFAULT 1
        );
        """

        self.fac_db.create_table(fac_conf_query)
        self.fac_db.create_table(menu_conf_query)
        self.fac_db.ensure_menu_config()

    def check_if_empty_database(self):
        load_query = """SELECT * FROM fac_config"""
        result = self.fac_db.read_val(load_query)
        if len(result) > 0:
            f_name = result[0][1]
            t_num = result[0][2]
            s_num = result[0][3]

            if f_name and t_num and s_num:
                self.fc_load_btn.config(state=tk.ACTIVE)
            else:
                self.fc_load_btn.config(state=tk.DISABLED)
                self.tr_view_remove.config(state=tk.DISABLED)

    def check_if_empty_fc_entry(self):
        f_name = self.fc_name_ent.get()
        t_num = self.fc_table_num_ent.get()
        s_num = self.fc_seat_num_ent.get()

        if f_name and t_num and s_num:
            self.fc_clear_btn.config(state=tk.ACTIVE)
        else:
            self.fc_clear_btn.config(state=tk.DISABLED)

    def is_product_available(self, pr_id):
        try:
            res = self.fac_db.read_val(
                """SELECT available FROM menu_config WHERE id = ?""", (pr_id,))
        except Exception as e:
            print(e)
            return True
        return bool(res and res[0][0])

    def sync_availability_buttons(self):
        try:
            selection = self.tr_view.selection()
            if not selection:
                self.sold_out_btn.config(state=tk.DISABLED)
                self.available_btn.config(state=tk.DISABLED)
                self.restore_all_btn.config(state=tk.DISABLED)
                return
            self.restore_all_btn.config(state=tk.ACTIVE)
            if self.is_product_available(selection[0]):
                self.sold_out_btn.config(state=tk.ACTIVE)
                self.available_btn.config(state=tk.DISABLED)
            else:
                self.sold_out_btn.config(state=tk.DISABLED)
                self.available_btn.config(state=tk.ACTIVE)
        except tk.TclError as e:
            print(e)

    def set_product_available(self, available):
        selection = self.tr_view.selection()
        if not selection:
            return
        pr_id = selection[0]
        update_query = """UPDATE menu_config SET available = ? WHERE id = ?"""
        self.fac_db.update(update_query, (1 if available else 0, pr_id))
        self.refresh_menu_items(keep_selection=pr_id)

    def restore_all_products(self):
        try:
            self.fac_db.update("UPDATE menu_config SET available = 1", ())
        except Exception as e:
            print(e)
            return
        self.refresh_menu_items()

    def refresh_menu_items(self, keep_selection=None):
        for child in self.tr_view.get_children():
            self.tr_view.delete(child)
        self.retreive_menu_items(keep_selection=keep_selection)

    def product_selected(self, event=None):
        try:
            selected_item = self.tr_view.selection()[0]
            sel_item_val = self.tr_view.item(selected_item)['values']
            sel_pr_txt = f"{sel_item_val[0]}) {sel_item_val[1]} {sel_item_val[2]}"
            self.sel_pr_id_lbl.config(text="")
            self.sel_pr_id_lbl.config(text=sel_pr_txt)
            self.tr_view_remove.config(state=tk.ACTIVE)
            self.avail_prd_lbl.config(text="Product Selected:")
        except IndexError as e:
            print(e)
        self.sync_availability_buttons()

    def fac_conf_clear(self):
        self.fc_name_ent.delete(0, tk.END)
        self.fc_seat_num_ent.delete(0, tk.END)
        self.fc_table_num_ent.delete(0, tk.END)

        self.fc_clear_btn.config(state=tk.DISABLED)

    def _show_input_error_once(self, flag, title, msg):
        if getattr(self, flag, False):
            return
        setattr(self, flag, True)

        def _show():
            try:
                messagebox.showerror(title, msg)
            finally:
                try:
                    setattr(self, flag, False)
                except tk.TclError:
                    pass
        try:
            self.after_idle(_show)
        except tk.TclError:
            setattr(self, flag, False)

    def callback_table(self, P):
        # Never raise or pop up a dialog from inside a validatecommand:
        # that freezes Tk and leaves the window blank/unpainted.
        if P == "":
            return True
        if not P.isdigit():
            self.bell()
            return False
        try:
            if int(P) > 50:
                self.bell()
                self._show_input_error_once(
                    "_table_err_pending", "Input Error",
                    "Maximum number of tables must not exceed 50!")
                return False
        except (ValueError, tk.TclError):
            return False
        return True

    def callback_seats(self, P):
        if P == "":
            return True
        if not P.isdigit():
            self.bell()
            return False
        try:
            raw = self.fc_table_num_ent.get()
            tables = int(raw) if raw.strip() != "" else 50
        except (ValueError, tk.TclError):
            # Tables field empty/invalid (e.g. during typing or Load/Clear):
            # fall back to absolute max (50 tables * 8 seats) instead of
            # raising ValueError which would break validation.
            tables = 50
        max_seats = max(0, tables) * 8
        try:
            ok = int(P) <= max_seats
        except ValueError:
            return False
        if not ok:
            self.bell()
            self._show_input_error_once(
                "_seats_err_pending", "Input Error",
                f"Maximum number of seats cannot exceed {max_seats}")
        return ok

    def validate_product(self, price, name):
        if (self.is_float(price) and float(price) <= 10000000) and (len(name) <= 20):
            return True
        elif (self.is_float(price) and float(price) > 10000000) and (len(name) <= 20):
            usr_resp = messagebox.askyesno(
                "Overprice Check", "The price you have entered exceeds maximum allowed (10 million Forints), do you wish to continue?")
            if usr_resp:
                return True
            else:
                self.food_price_entry.delete(0, tk.END)
                return False
        elif (self.is_float(price) and float(price) > 10000000) and (len(name) > 20):
            usr_resp = messagebox.showerror(
                "Wrong inputs", "The price you have entered exceeds maximum allowed (10 million Forints) and product name should be less than 20 characters long")
            self.food_price_entry.delete(0, tk.END)
            self.food_name_entry.delete(0, tk.END)
            return False
        else:
            messagebox.showerror(
                "Wrong input", "Please enter the product name(max. 20 characters long) and price(max 10 mln forints) correctly!")
            return False

    def save_fac_config(self):
        load_query = """SELECT * FROM fac_config"""
        result = self.fac_db.read_val(load_query)

        fac_name = self.fc_name_ent.get()
        table_num = self.fc_table_num_ent.get()
        seat_num = self.fc_seat_num_ent.get()

        if fac_name and table_num and seat_num:
            if len(result) >= 1:
                update_query = """UPDATE fac_config
                SET fac_name = ?,
                table_num = ?,
                seat_num = ?
                WHERE id = ?
                """
                self.fac_db.update(
                    update_query, (fac_name, table_num, seat_num, 1))
            else:
                spec_insert_query = """INSERT INTO fac_config VALUES (?, ?, ?, ?)"""
                self.fac_db.insert_spec_config(
                    spec_insert_query, (1, fac_name, table_num, seat_num))
            self.check_if_empty_database()
            self.check_if_empty_fc_entry()
        else:
            messagebox.showerror(
                "Empty input fields", "Please enter facility name, table number and seat number accordingly!")

    def load_fac_config(self):
        self.fac_conf_clear()
        load_query = """SELECT * FROM fac_config"""
        result = self.fac_db.read_val(load_query)

        self.fc_name_ent.insert(0, result[0][1])
        self.fc_table_num_ent.insert(0, result[0][2])
        self.fc_seat_num_ent.insert(0, result[0][3])
        self.check_if_empty_fc_entry()

    def remove_selected(self, event=""):
        try:
            selected_item = self.tr_view.selection()
            sel_it_ind = selected_item[0]
            delete_query = """DELETE FROM menu_config WHERE id = ?"""
            self.fac_db.delete_val(delete_query, [sel_it_ind])
            for sel_item in selected_item:
                self.tr_view.delete(sel_item)
            self.sel_pr_id_lbl.config(text="")
            self.tr_view_remove.config(state=tk.DISABLED)
            self.sync_availability_buttons()
        except IndexError as e:
            print(e)

    def add_record(self, event='<Return>'):
        food_name = self.food_name_entry.get()
        food_price = self.food_price_entry.get()
        spec_insert_query = """INSERT INTO menu_config
                (id, product_name, product_price, available)
                VALUES (?, ?, ?, ?)"""
        pr_id = self.get_product_id()
        pr_ind = pr_id if pr_id == 1 else int(pr_id) + 1
        if food_name and food_price:
            validate_product = self.validate_product(food_price, food_name)
            if validate_product:
                self.tr_view.insert("", tk.END, iid=f"{pr_ind}", values=(
                    pr_ind, food_name, f"{float(food_price):.2f}", "Available"))

                self.fac_db.insert_spec_config(
                    spec_insert_query, (pr_ind, food_name, food_price, 1))
        else:
            er_msg = "Please fill \"Name of the product \" and \"Price of the product\" fields!"
            messagebox.showerror("Empty input fields", er_msg)

        self.food_name_entry.delete(0, tk.END)
        self.food_price_entry.delete(0, tk.END)

    def is_float(self, element):
        if element is None:
            return False
        try:
            float(element)
            return True
        except ValueError:
            return False

    def destroy(self):
        self.func()
        super().destroy()

    def __del__(self):
        self.func()
