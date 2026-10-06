
import sqlite3
from sqlite3 import Error


class Database:
    def __init__(self, db):
        self.conn = sqlite3.connect(db)
        self.cur = self.conn.cursor()
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS gen_config (id INTEGER PRIMARY KEY, conf_name text);")
        self.conn.commit()

        self.insert_genconfig()

    def create_table(self, create_table_query):
        try:
            cursor = self.cur
            cursor.execute(create_table_query)
            self.conn.commit()
        except Error as e:
            print(e)

    def ensure_cooked_orders(self):
        self.create_table("""
        CREATE TABLE IF NOT EXISTS cooked_orders(
            id integer PRIMARY KEY,
            table_num integer NOT NULL,
            product_name text NOT NULL,
            order_quantity integer NOT NULL,
            order_price integer NOT NULL,
            bill_id integer,
            billed integer NOT NULL DEFAULT 0
        );
        """)
        columns = {r[1] for r in self.read_val("PRAGMA table_info(cooked_orders)")}
        if "bill_id" not in columns:
            self.add_column("cooked_orders", "bill_id integer")
        if "billed" not in columns:
            self.add_column(
                "cooked_orders", "billed integer NOT NULL DEFAULT 0")
        self.backfill_bills()

    def ensure_menu_config(self):
        self.create_table("""
        CREATE TABLE IF NOT EXISTS menu_config(
            id integer PRIMARY KEY,
            product_name text NOT NULL,
            product_price real NOT NULL,
            available integer NOT NULL DEFAULT 1
        );
        """)
        columns = {r[1] for r in self.read_val("PRAGMA table_info(menu_config)")}
        if "available" not in columns:
            self.add_column(
                "menu_config", "available integer NOT NULL DEFAULT 1")
        self.backfill_availability()

    def backfill_availability(self):
        try:
            self.cur.execute(
                "UPDATE menu_config SET available = 1 WHERE available IS NULL")
            self.conn.commit()
        except Error as e:
            print(e)

    def add_column(self, table_name, column_def):
        try:
            self.cur.execute(
                f"ALTER TABLE {table_name} ADD COLUMN {column_def}")
            self.conn.commit()
        except Error as e:
            print(e)

    def backfill_bills(self):
        try:
            self.cur.execute("""
                UPDATE cooked_orders
                SET bill_id = (
                    SELECT MIN(older.id) FROM cooked_orders AS older
                    WHERE older.table_num = cooked_orders.table_num
                )
                WHERE bill_id IS NULL
                """)
            self.cur.execute(
                "UPDATE cooked_orders SET billed = 1 WHERE billed IS NULL")
            self.conn.commit()
        except Error as e:
            print(e)

    def next_bill_id(self):
        rows = self.read_val("SELECT MAX(bill_id) FROM cooked_orders")
        current = rows[0][0] if rows and rows[0][0] is not None else 0
        return current + 1

    def insert_genconfig(self):
        try:
            self.cur.execute("INSERT OR IGNORE INTO gen_config(id, conf_name) VALUES (?, ?)",
                             (1, "fac_config"))
            self.cur.execute("INSERT OR IGNORE INTO gen_config(id, conf_name) VALUES (?, ?)",
                             (2, "menu_config"))
            self.cur.execute("INSERT OR IGNORE INTO gen_config(id, conf_name) VALUES (?, ?)",
                             (3, "orders"))
            self.conn.commit()
        except Error as e:
            print(e)

    def insert_spec_config(self, insert_query, values):
        try:
            con = self.cur
            con.execute(insert_query, values)
            self.conn.commit()
        except Error as e:
            print(e)

    def update(self, update_query, values):
        try:
            con = self.cur
            con.execute(update_query, values)
            self.conn.commit()
        except Error as e:
            print(e)

    def read_val(self, read_query, table_num=''):
        try:
            con = self.cur
            if "WHERE" in read_query:
                con.execute(read_query, table_num)
                rows = con.fetchall()
            else:
                con.execute(read_query)
                rows = con.fetchall()
            return rows
        except Error as e:
            if "no such table" in str(e):
                return []
            print(e)
            return []

    def delete_val(self, delete_query, item_id):
        try:
            con = self.cur
            con.execute(delete_query, item_id)
            self.conn.commit()
        except Error as e:
            print(e)

    def __del__(self):
        conn = getattr(self, "conn", None)
        if conn is None:
            return
        try:
            conn.close()
        except Error:
            pass
