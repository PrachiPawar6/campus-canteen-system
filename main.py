import tkinter as tk
from tkinter import ttk
from views.login_view import LoginView
from views.admin_view import AdminDashboardView
from views.student_view import StudentDashboardView
from database import init_db

class CanteenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Campus Canteen System")
        self.root.geometry("900x600")
        
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")
            
        style.configure("TNotebook.Tab", font=("Arial", 11, "bold"), padding=[10, 5])
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.configure("Treeview", font=("Arial", 10), rowheight=25)
        
        # Ensure database is initialized before the app starts
        init_db()
        
        self.current_user = None
        self.current_frame = None
        
        # Start by showing the login screen
        self.show_login_screen()

    def show_login_screen(self):
        """Displays the Login/Registration screen."""
        self.clear_frame()
        self.current_frame = LoginView(self.root, self.on_login_success)
        self.current_frame.pack(expand=True, fill="both", padx=20, pady=20)

    def on_login_success(self, user):
        """
        Callback function executed when a user successfully logs in.
        user is a dictionary containing user details from the database.
        """
        self.current_user = user
        if user['role'] == 'admin':
            self.show_admin_dashboard()
        else:
            self.show_student_dashboard()

    def show_admin_dashboard(self):
        """Displays the Admin Dashboard screen."""
        self.clear_frame()
        self.current_frame = AdminDashboardView(self.root, self, self.current_user)
        self.current_frame.pack(expand=True, fill="both")

    def show_student_dashboard(self):
        """Displays the Student Dashboard screen."""
        self.clear_frame()
        self.current_frame = StudentDashboardView(self.root, self, self.current_user)
        self.current_frame.pack(expand=True, fill="both")

    def clear_frame(self):
        """Removes the currently displayed frame to make room for a new one."""
        if self.current_frame is not None:
            self.current_frame.destroy()
            self.current_frame = None

if __name__ == "__main__":
    # Create the main Tkinter window
    root = tk.Tk()
    
    # Instantiate our application class
    app = CanteenApp(root)
    
    # Start the Tkinter event loop
    root.mainloop()
