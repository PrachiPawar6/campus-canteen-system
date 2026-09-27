import tkinter as tk
from tkinter import ttk, messagebox
from models.user import authenticate_user, register_user

class LoginView(ttk.Frame):
    def __init__(self, parent, on_login_success):
        """
        Initialize the login frame.
        parent: The root window or parent frame.
        on_login_success: A function to call when login is successful.
        """
        super().__init__(parent, padding="20 20 20 20")
        self.on_login_success = on_login_success
        
        # Configure layout
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        
        # Title
        title = ttk.Label(self, text="Campus Canteen System", font=("Arial", 24, "bold"))
        title.grid(row=0, column=0, columnspan=2, pady=(0, 30))
        
        # Username Label & Entry
        ttk.Label(self, text="Username:", font=("Arial", 12)).grid(row=1, column=0, pady=10, sticky="e")
        self.username_entry = ttk.Entry(self, font=("Arial", 12), width=25)
        self.username_entry.grid(row=1, column=1, pady=10, padx=10, sticky="w")
        
        # Password Label & Entry
        ttk.Label(self, text="Password:", font=("Arial", 12)).grid(row=2, column=0, pady=10, sticky="e")
        self.password_entry = ttk.Entry(self, font=("Arial", 12), show="*", width=25)
        self.password_entry.grid(row=2, column=1, pady=10, padx=10, sticky="w")
        
        # Login Button
        login_btn = ttk.Button(self, text="Login", command=self.handle_login)
        login_btn.grid(row=3, column=0, columnspan=2, pady=(20, 10))
        
        # Divider or spacing
        ttk.Label(self, text="--- OR ---", font=("Arial", 10)).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Register Button
        register_btn = ttk.Button(self, text="Register as Student", command=self.handle_register)
        register_btn.grid(row=5, column=0, columnspan=2, pady=10)
        
    def handle_login(self):
        """Called when the user clicks the Login button."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Error", "Please enter both username and password.")
            return
            
        user = authenticate_user(username, password)
        
        if user:
            # Login successful
            messagebox.showinfo("Success", f"Login successful!\nYou are logged in as: {user['role'].capitalize()}")
            # Call the callback function passed from main.py
            self.on_login_success(user)
        else:
            # Login failed
            messagebox.showerror("Error", "Invalid username or password.")
            
    def handle_register(self):
        """Called when the user clicks the Register button."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showwarning("Error", "Please enter a username and password to register.")
            return
            
        # By default, we register new users as 'student'
        success, message = register_user(username, password, role="student")
        
        if success:
            messagebox.showinfo("Success", message + " You can now log in.")
            # Clear fields after successful registration
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", message)
