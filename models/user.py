import sqlite3
from database import get_connection

def authenticate_user(username, password):
    """
    Checks if the username and password match.
    Returns the user data as a dictionary if successful, else None.
    """
    conn = get_connection()
    conn.row_factory = sqlite3.Row # This allows us to access columns by name
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    
    conn.close()
    
    if user:
        return dict(user)
    return None

def register_user(username, password, role="student"):
    """
    Registers a new user in the database.
    Returns a tuple (success: bool, message: str)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO Users (username, password, role) VALUES (?, ?, ?)",
            (username, password, role)
        )
        conn.commit()
        return True, "Registration successful."
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    except Exception as e:
        return False, f"An error occurred: {str(e)}"
    finally:
        conn.close()
