import tkinter as tk
from tkinter import ttk, messagebox
from models.menu import get_all_menu_items, add_menu_item, update_menu_item, delete_menu_item
from models.order import get_all_orders, update_order_status

class AdminDashboardView(tk.Frame):
    def __init__(self, parent, controller, current_user):
        super().__init__(parent)
        self.controller = controller
        self.current_user = current_user
        
        self.selected_item_id = None
        self.selected_order_id = None
        self.orders = [] # Cache for order details
        
        self._build_ui()
        self.load_menu_data()
        self.load_order_data()

    def _build_ui(self):
        # Header bar
        header_frame = tk.Frame(self, pady=10)
        header_frame.pack(fill="x", padx=15)
        
        lbl_welcome = tk.Label(
            header_frame, 
            text=f"Admin Dashboard - Logged in as: {self.current_user['username']}", 
            font=("Arial", 14, "bold")
        )
        lbl_welcome.pack(side="left")
        
        btn_logout = tk.Button(header_frame, text="Logout", command=self.logout)
        btn_logout.pack(side="right")

        # Main layout: Notebook for Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=10)

        # ==========================================
        # TAB 1: MENU MANAGEMENT
        # ==========================================
        tab_menu = ttk.Frame(self.notebook)
        self.notebook.add(tab_menu, text="Menu Management")

        # --- LEFT: Form Frame ---
        form_frame = tk.LabelFrame(tab_menu, text="Manage Item", padx=10, pady=10)
        form_frame.pack(side="left", fill="y", padx=(0, 10), pady=10)

        tk.Label(form_frame, text="Item Name:").pack(anchor="w", pady=(5, 0))
        self.entry_name = tk.Entry(form_frame, width=25)
        self.entry_name.pack(fill="x", pady=2)

        tk.Label(form_frame, text="Category:").pack(anchor="w", pady=(5, 0))
        self.combo_category = ttk.Combobox(
            form_frame, 
            values=["Snacks", "Beverages", "Meals", "Bakery"], 
            state="readonly"
        )
        self.combo_category.set("Snacks")
        self.combo_category.pack(fill="x", pady=2)

        tk.Label(form_frame, text="Price (₹):").pack(anchor="w", pady=(5, 0))
        self.entry_price = tk.Entry(form_frame, width=25)
        self.entry_price.pack(fill="x", pady=2)

        tk.Label(form_frame, text="Description:").pack(anchor="w", pady=(5, 0))
        self.entry_desc = tk.Entry(form_frame, width=25)
        self.entry_desc.pack(fill="x", pady=2)

        self.var_available = tk.BooleanVar(value=True)
        self.chk_available = tk.Checkbutton(form_frame, text="Available for Order", variable=self.var_available)
        self.chk_available.pack(anchor="w", pady=(10, 10))

        # Form Buttons
        btn_add = tk.Button(form_frame, text="Add New Item", bg="#d4edda", command=self.handle_add)
        btn_add.pack(fill="x", pady=3)

        btn_update = tk.Button(form_frame, text="Update Selected", bg="#fff3cd", command=self.handle_update)
        btn_update.pack(fill="x", pady=3)

        btn_delete = tk.Button(form_frame, text="Delete Selected", bg="#f8d7da", command=self.handle_delete)
        btn_delete.pack(fill="x", pady=3)

        btn_clear = tk.Button(form_frame, text="Clear Form", command=self.clear_form)
        btn_clear.pack(fill="x", pady=3)

        # --- RIGHT: Treeview Table ---
        table_frame = tk.Frame(tab_menu, pady=10)
        table_frame.pack(side="right", fill="both", expand=True)

        columns = ("id", "name", "category", "price", "available", "description")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("category", text="Category")
        self.tree.heading("price", text="Price (₹)")
        self.tree.heading("available", text="Status")
        self.tree.heading("description", text="Description")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("name", width=120)
        self.tree.column("category", width=90)
        self.tree.column("price", width=70, anchor="e")
        self.tree.column("available", width=80, anchor="center")
        self.tree.column("description", width=160)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_item_select)

        # ==========================================
        # TAB 2: ORDER MANAGEMENT
        # ==========================================
        tab_orders = ttk.Frame(self.notebook)
        self.notebook.add(tab_orders, text="Order Management")
        
        # --- TOP: Orders Table ---
        orders_top_frame = tk.Frame(tab_orders, pady=10)
        orders_top_frame.pack(fill="both", expand=True)
        
        order_cols = ("id", "token", "user", "total", "status", "time")
        self.orders_tree = ttk.Treeview(orders_top_frame, columns=order_cols, show="headings", selectmode="browse")
        
        self.orders_tree.heading("id", text="Order ID")
        self.orders_tree.heading("token", text="Token Number")
        self.orders_tree.heading("user", text="Student")
        self.orders_tree.heading("total", text="Total (₹)")
        self.orders_tree.heading("status", text="Status")
        self.orders_tree.heading("time", text="Timestamp")
        
        self.orders_tree.column("id", width=60, anchor="center")
        self.orders_tree.column("token", width=100, anchor="center")
        self.orders_tree.column("user", width=100)
        self.orders_tree.column("total", width=80, anchor="e")
        self.orders_tree.column("status", width=100, anchor="center")
        self.orders_tree.column("time", width=150)
        
        orders_scroll = ttk.Scrollbar(orders_top_frame, orient="vertical", command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=orders_scroll.set)
        
        self.orders_tree.pack(side="left", fill="both", expand=True)
        orders_scroll.pack(side="right", fill="y")
        
        self.orders_tree.bind("<<TreeviewSelect>>", self.on_order_select)
        
        # --- BOTTOM: Order Details & Actions ---
        orders_bottom_frame = tk.Frame(tab_orders, pady=10)
        orders_bottom_frame.pack(fill="x")
        
        # Details text box
        self.txt_order_details = tk.Text(orders_bottom_frame, height=5, width=40, state="disabled")
        self.txt_order_details.pack(side="left", padx=(0, 15))
        
        # Action buttons
        actions_frame = tk.LabelFrame(orders_bottom_frame, text="Update Status", padx=10, pady=10)
        actions_frame.pack(side="left", fill="y")
        
        btn_prep = tk.Button(actions_frame, text="Mark Preparing", bg="#fff3cd", width=15, 
                             command=lambda: self.handle_status_update("Preparing"))
        btn_prep.grid(row=0, column=0, padx=5, pady=5)
        
        btn_ready = tk.Button(actions_frame, text="Mark Ready", bg="#d4edda", width=15, 
                              command=lambda: self.handle_status_update("Ready"))
        btn_ready.grid(row=0, column=1, padx=5, pady=5)
        
        btn_collected = tk.Button(actions_frame, text="Mark Collected", bg="#cce5ff", width=15, 
                                  command=lambda: self.handle_status_update("Collected"))
        btn_collected.grid(row=0, column=2, padx=5, pady=5)
        
        btn_refresh = tk.Button(orders_bottom_frame, text="Refresh Orders", font=("Arial", 10, "bold"), 
                                command=self.load_order_data)
        btn_refresh.pack(side="right", padx=10)

        # ==========================================
        # TAB 3: SALES SUMMARY
        # ==========================================
        tab_summary = ttk.Frame(self.notebook)
        self.notebook.add(tab_summary, text="Sales Summary")
        
        summary_container = tk.Frame(tab_summary, pady=40)
        summary_container.pack(fill="both", expand=True)
        
        self.lbl_total_orders = tk.Label(
            summary_container, 
            text="Total Orders: 0", 
            font=("Arial", 24, "bold"),
            fg="#333333"
        )
        self.lbl_total_orders.pack(pady=20)
        
        self.lbl_total_revenue = tk.Label(
            summary_container, 
            text="Total Revenue: ₹0.00", 
            font=("Arial", 24, "bold"),
            fg="#28a745"
        )
        self.lbl_total_revenue.pack(pady=20)
        
        btn_refresh_summary = tk.Button(
            summary_container, 
            text="Refresh Summary", 
            font=("Arial", 12, "bold"), 
            command=self.load_order_data,
            bg="#e2e6ea",
            padx=20,
            pady=10
        )
        btn_refresh_summary.pack(pady=30)
    # ==========================================
    # MENU MANAGEMENT METHODS
    # ==========================================
    def load_menu_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        items = get_all_menu_items()
        for itm in items:
            status_text = "Available" if itm["is_available"] else "Sold Out"
            self.tree.insert("", "end", values=(
                itm["item_id"], 
                itm["name"], 
                itm["category"], 
                f"{itm['price']:.2f}", 
                status_text, 
                itm["description"]
            ))

    def on_item_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        
        values = self.tree.item(selected[0], "values")
        self.selected_item_id = int(values[0])

        self.entry_name.delete(0, tk.END)
        self.entry_name.insert(0, values[1])
        self.combo_category.set(values[2])
        self.entry_price.delete(0, tk.END)
        self.entry_price.insert(0, values[3])
        self.var_available.set(True if values[4] == "Available" else False)
        self.entry_desc.delete(0, tk.END)
        self.entry_desc.insert(0, values[5])

    def handle_add(self):
        name = self.entry_name.get().strip()
        category = self.combo_category.get()
        desc = self.entry_desc.get().strip()
        try: price = float(self.entry_price.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric price.")
            return
        if not name:
            messagebox.showerror("Error", "Item name cannot be empty.")
            return

        success, message = add_menu_item(name, desc, price, category, self.var_available.get())
        if success:
            messagebox.showinfo("Success", f"'{name}' added to menu.")
            self.clear_form()
            self.load_menu_data()
        else:
            messagebox.showerror("Error", message)

    def handle_update(self):
        if not self.selected_item_id:
            messagebox.showwarning("Warning", "Select an item from the table first.")
            return
        name = self.entry_name.get().strip()
        category = self.combo_category.get()
        desc = self.entry_desc.get().strip()
        try: price = float(self.entry_price.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric price.")
            return

        success, message = update_menu_item(self.selected_item_id, name, desc, price, category, self.var_available.get())
        if success:
            messagebox.showinfo("Success", "Item updated successfully.")
            self.clear_form()
            self.load_menu_data()
        else:
            messagebox.showerror("Error", message)

    def handle_delete(self):
        if not self.selected_item_id:
            messagebox.showwarning("Warning", "Select an item from the table first.")
            return
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this menu item?")
        if confirm:
            success, message = delete_menu_item(self.selected_item_id)
            if success:
                messagebox.showinfo("Deleted", "Item removed successfully.")
                self.clear_form()
                self.load_menu_data()
            else:
                messagebox.showerror("Error", message)

    def clear_form(self):
        self.selected_item_id = None
        self.entry_name.delete(0, tk.END)
        self.entry_price.delete(0, tk.END)
        self.entry_desc.delete(0, tk.END)
        self.combo_category.set("Snacks")
        self.var_available.set(True)
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection())

    # ==========================================
    # ORDER MANAGEMENT METHODS
    # ==========================================
    def load_order_data(self):
        self.orders = get_all_orders()
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)
            
        total_revenue = 0.0
        total_orders = 0
            
        for order in self.orders:
            self.orders_tree.insert("", "end", iid=str(order['order_id']), values=(
                order['order_id'],
                order['token_number'],
                order['username'],
                f"{order['total_amount']:.2f}",
                order['status'],
                order['timestamp']
            ))
            
            # Count only completed or all orders? Let's count all that are not 'Cancelled' (we don't have Cancelled)
            # Or we can just calculate total revenue
            total_revenue += order['total_amount']
            total_orders += 1
            
        # Update Sales Summary Tab
        if hasattr(self, 'lbl_total_orders') and hasattr(self, 'lbl_total_revenue'):
            self.lbl_total_orders.config(text=f"Total Orders: {total_orders}")
            self.lbl_total_revenue.config(text=f"Total Revenue: ₹{total_revenue:.2f}")

        self.show_order_details(None)

    def on_order_select(self, event):
        selected = self.orders_tree.selection()
        if not selected:
            self.selected_order_id = None
            self.show_order_details(None)
            return
            
        self.selected_order_id = int(selected[0])
        # Find order details
        for order in self.orders:
            if order['order_id'] == self.selected_order_id:
                self.show_order_details(order)
                break

    def show_order_details(self, order):
        self.txt_order_details.config(state="normal")
        self.txt_order_details.delete("1.0", tk.END)
        
        if order:
            self.txt_order_details.insert(tk.END, f"Token: {order['token_number']} | Student: {order['username']}\n")
            self.txt_order_details.insert(tk.END, "-"*40 + "\n")
            for item in order['items']:
                self.txt_order_details.insert(tk.END, f"{item['quantity']}x {item['name']}\n")
        else:
            self.txt_order_details.insert(tk.END, "Select an order to view items.")
            
        self.txt_order_details.config(state="disabled")

    def handle_status_update(self, new_status):
        if not self.selected_order_id:
            messagebox.showwarning("Warning", "Select an order from the table first.")
            return
            
        success, message = update_order_status(self.selected_order_id, new_status)
        if success:
            messagebox.showinfo("Success", f"Order status updated to {new_status}")
            self.load_order_data()
        else:
            messagebox.showerror("Error", message)

    def logout(self):
        self.controller.show_login_screen()
