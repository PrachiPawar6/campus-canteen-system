import tkinter as tk
from tkinter import ttk, messagebox
from models.menu import get_all_menu_items
from models.order import place_order, get_orders_by_user

class StudentDashboardView(tk.Frame):
    def __init__(self, parent, controller, current_user):
        super().__init__(parent)
        self.controller = controller
        self.current_user = current_user
        
        # cart will hold dictionaries: {'item_id': id, 'name': name, 'price': price, 'quantity': qty}
        self.cart = []
        self.my_orders = []
        
        self._build_ui()
        self.load_menu_data()
        self.load_my_orders()

    def _build_ui(self):
        # Header bar
        header_frame = tk.Frame(self, pady=10)
        header_frame.pack(fill="x", padx=15)
        
        lbl_welcome = tk.Label(
            header_frame, 
            text=f"Student Dashboard - Logged in as: {self.current_user['username']}", 
            font=("Arial", 14, "bold")
        )
        lbl_welcome.pack(side="left")
        
        btn_logout = tk.Button(header_frame, text="Logout", command=self.logout)
        btn_logout.pack(side="right")
        
        # Main layout: Notebook for Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=10)

        # ==========================================
        # TAB 1: ORDER FOOD
        # ==========================================
        tab_order = ttk.Frame(self.notebook)
        self.notebook.add(tab_order, text="Order Food")

        # --- LEFT: Menu Catalog ---
        menu_frame = tk.LabelFrame(tab_order, text="Available Menu", padx=10, pady=10)
        menu_frame.pack(side="left", fill="both", expand=True, padx=(0, 10), pady=10)
        
        columns = ("id", "name", "category", "price", "description")
        self.menu_tree = ttk.Treeview(menu_frame, columns=columns, show="headings", selectmode="browse")
        
        self.menu_tree.heading("id", text="ID")
        self.menu_tree.heading("name", text="Name")
        self.menu_tree.heading("category", text="Category")
        self.menu_tree.heading("price", text="Price (₹)")
        self.menu_tree.heading("description", text="Description")
        
        self.menu_tree.column("id", width=30, anchor="center")
        self.menu_tree.column("name", width=120)
        self.menu_tree.column("category", width=80)
        self.menu_tree.column("price", width=60, anchor="e")
        self.menu_tree.column("description", width=150)
        
        menu_scrollbar = ttk.Scrollbar(menu_frame, orient="vertical", command=self.menu_tree.yview)
        self.menu_tree.configure(yscrollcommand=menu_scrollbar.set)
        
        self.menu_tree.pack(side="top", fill="both", expand=True)
        menu_scrollbar.pack(side="right", fill="y")
        
        # Add to Cart area
        add_frame = tk.Frame(menu_frame, pady=10)
        add_frame.pack(fill="x")
        
        tk.Label(add_frame, text="Quantity:").pack(side="left", padx=5)
        self.entry_quantity = tk.Entry(add_frame, width=5)
        self.entry_quantity.insert(0, "1")
        self.entry_quantity.pack(side="left", padx=5)
        
        btn_add = tk.Button(add_frame, text="Add to Cart", bg="#d4edda", command=self.handle_add_to_cart)
        btn_add.pack(side="left", padx=15)
        
        # --- RIGHT: Cart Area ---
        cart_frame = tk.LabelFrame(tab_order, text="Your Cart", padx=10, pady=10)
        cart_frame.pack(side="right", fill="both", expand=True, pady=10)
        
        cart_columns = ("name", "quantity", "price", "subtotal")
        self.cart_tree = ttk.Treeview(cart_frame, columns=cart_columns, show="headings", selectmode="browse")
        
        self.cart_tree.heading("name", text="Item")
        self.cart_tree.heading("quantity", text="Qty")
        self.cart_tree.heading("price", text="Price")
        self.cart_tree.heading("subtotal", text="Subtotal")
        
        self.cart_tree.column("name", width=120)
        self.cart_tree.column("quantity", width=40, anchor="center")
        self.cart_tree.column("price", width=50, anchor="e")
        self.cart_tree.column("subtotal", width=60, anchor="e")
        
        self.cart_tree.pack(side="top", fill="both", expand=True)
        
        # Cart actions
        cart_action_frame = tk.Frame(cart_frame, pady=10)
        cart_action_frame.pack(fill="x")
        
        btn_remove = tk.Button(cart_action_frame, text="Remove Selected", command=self.handle_remove_from_cart)
        btn_remove.pack(side="left")
        
        self.lbl_total = tk.Label(cart_action_frame, text="Total: ₹0.00", font=("Arial", 12, "bold"))
        self.lbl_total.pack(side="right", padx=15)
        
        btn_checkout = tk.Button(cart_frame, text="Place Order", bg="#cce5ff", font=("Arial", 12, "bold"), pady=5, command=self.handle_checkout)
        btn_checkout.pack(fill="x", pady=(10, 0))

        # ==========================================
        # TAB 2: MY ORDERS
        # ==========================================
        tab_history = ttk.Frame(self.notebook)
        self.notebook.add(tab_history, text="My Orders")

        # --- TOP: Orders Table ---
        history_top_frame = tk.Frame(tab_history, pady=10)
        history_top_frame.pack(fill="both", expand=True)
        
        history_cols = ("id", "token", "total", "status", "time")
        self.history_tree = ttk.Treeview(history_top_frame, columns=history_cols, show="headings", selectmode="browse")
        
        self.history_tree.heading("id", text="Order ID")
        self.history_tree.heading("token", text="Token Number")
        self.history_tree.heading("total", text="Total (₹)")
        self.history_tree.heading("status", text="Status")
        self.history_tree.heading("time", text="Timestamp")
        
        self.history_tree.column("id", width=60, anchor="center")
        self.history_tree.column("token", width=100, anchor="center")
        self.history_tree.column("total", width=80, anchor="e")
        self.history_tree.column("status", width=100, anchor="center")
        self.history_tree.column("time", width=150)
        
        history_scroll = ttk.Scrollbar(history_top_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=history_scroll.set)
        
        self.history_tree.pack(side="left", fill="both", expand=True)
        history_scroll.pack(side="right", fill="y")
        
        self.history_tree.bind("<<TreeviewSelect>>", self.on_history_select)

        # --- BOTTOM: Order Details & Actions ---
        history_bottom_frame = tk.Frame(tab_history, pady=10)
        history_bottom_frame.pack(fill="x")
        
        # Details text box
        self.txt_history_details = tk.Text(history_bottom_frame, height=5, width=40, state="disabled")
        self.txt_history_details.pack(side="left", padx=(0, 15))

        btn_refresh = tk.Button(history_bottom_frame, text="Refresh Status", font=("Arial", 10, "bold"), 
                                command=self.load_my_orders)
        btn_refresh.pack(side="right", padx=10)


    # ==========================================
    # ORDER FOOD METHODS
    # ==========================================
    def load_menu_data(self):
        for item in self.menu_tree.get_children():
            self.menu_tree.delete(item)
            
        items = get_all_menu_items(available_only=True)
        for itm in items:
            self.menu_tree.insert("", "end", values=(
                itm["item_id"], 
                itm["name"], 
                itm["category"], 
                f"{float(itm['price']):.2f}", 
                itm["description"]
            ))
            
    def update_cart_ui(self):
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
            
        total = 0.0
        for idx, item in enumerate(self.cart):
            subtotal = item['price'] * item['quantity']
            total += subtotal
            self.cart_tree.insert("", "end", iid=str(idx), values=(
                item['name'],
                item['quantity'],
                f"{item['price']:.2f}",
                f"{subtotal:.2f}"
            ))
            
        self.lbl_total.config(text=f"Total: ₹{total:.2f}")

    def handle_add_to_cart(self):
        selected = self.menu_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a menu item to add.")
            return
            
        try:
            qty = int(self.entry_quantity.get())
            if qty <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a positive integer.")
            return
            
        values = self.menu_tree.item(selected[0], "values")
        item_id = int(values[0])
        name = values[1]
        price = float(values[3])
        
        found = False
        for item in self.cart:
            if item['item_id'] == item_id:
                item['quantity'] += qty
                found = True
                break
                
        if not found:
            self.cart.append({'item_id': item_id, 'name': name, 'price': price, 'quantity': qty})
            
        self.update_cart_ui()
        self.entry_quantity.delete(0, tk.END)
        self.entry_quantity.insert(0, "1")
        
    def handle_remove_from_cart(self):
        selected = self.cart_tree.selection()
        if not selected:
            return
        idx = int(selected[0])
        del self.cart[idx]
        self.update_cart_ui()
        
    def handle_checkout(self):
        if not self.cart:
            messagebox.showwarning("Warning", "Your cart is empty.")
            return
            
        confirm = messagebox.askyesno("Confirm Order", "Are you sure you want to place this order? You will pay on collection.")
        if confirm:
            success, result = place_order(self.current_user['user_id'], self.cart)
            if success:
                token = result
                messagebox.showinfo(
                    "Order Successful", 
                    f"Your order has been placed successfully!\n\nYour Token Number is: {token}\n\nPlease show this at the counter."
                )
                self.cart = []
                self.update_cart_ui()
                self.load_my_orders() # Automatically refresh the history tab
            else:
                messagebox.showerror("Error", f"Failed to place order: {result}")

    # ==========================================
    # MY ORDERS METHODS
    # ==========================================
    def load_my_orders(self):
        self.my_orders = get_orders_by_user(self.current_user['user_id'])
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        for order in self.my_orders:
            self.history_tree.insert("", "end", iid=str(order['order_id']), values=(
                order['order_id'],
                order['token_number'],
                f"{order['total_amount']:.2f}",
                order['status'],
                order['timestamp']
            ))
        self.show_history_details(None)

    def on_history_select(self, event):
        selected = self.history_tree.selection()
        if not selected:
            self.show_history_details(None)
            return
            
        selected_id = int(selected[0])
        for order in self.my_orders:
            if order['order_id'] == selected_id:
                self.show_history_details(order)
                break

    def show_history_details(self, order):
        self.txt_history_details.config(state="normal")
        self.txt_history_details.delete("1.0", tk.END)
        
        if order:
            self.txt_history_details.insert(tk.END, f"Token: {order['token_number']} | Status: {order['status']}\n")
            self.txt_history_details.insert(tk.END, "-"*40 + "\n")
            for item in order['items']:
                self.txt_history_details.insert(tk.END, f"{item['quantity']}x {item['name']}\n")
        else:
            self.txt_history_details.insert(tk.END, "Select an order to view items.")
            
        self.txt_history_details.config(state="disabled")

    def logout(self):
        self.controller.show_login_screen()
