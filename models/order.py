import sqlite3
import random
import string
from database import get_connection

def generate_token():
    """Generates a random 4-character token (e.g., A5B2)."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

def place_order(user_id, cart_items):
    """
    Places a new order.
    cart_items should be a list of dictionaries: [{'item_id': 1, 'quantity': 2, 'price': 15.0}, ...]
    Returns tuple (success: bool, token_number_or_error_msg: str)
    """
    if not cart_items:
        return False, "Cart is empty."
        
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Calculate total amount
        total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
        token = generate_token()
        
        # Ensure token is unique (simple loop, though collision chance is low)
        while True:
            cursor.execute("SELECT COUNT(*) FROM Orders WHERE token_number = ?", (token,))
            if cursor.fetchone()[0] == 0:
                break
            token = generate_token()
            
        # Insert into Orders
        cursor.execute(
            "INSERT INTO Orders (user_id, total_amount, status, token_number) VALUES (?, ?, 'Pending', ?)",
            (user_id, total_amount, token)
        )
        order_id = cursor.lastrowid
        
        # Insert into OrderDetails
        for item in cart_items:
            cursor.execute(
                "INSERT INTO OrderDetails (order_id, item_id, quantity, price_at_order) VALUES (?, ?, ?, ?)",
                (order_id, item['item_id'], item['quantity'], item['price'])
            )
            
        conn.commit()
        return True, token
    except Exception as e:
        conn.rollback()
        return False, f"Error placing order: {str(e)}"
    finally:
        conn.close()

def get_orders_by_user(user_id):
    """Retrieves all orders for a specific user, along with item details."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Orders WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
    orders = [dict(row) for row in cursor.fetchall()]
    
    for order in orders:
        cursor.execute("""
            SELECT od.quantity, od.price_at_order, m.name 
            FROM OrderDetails od
            JOIN MenuItems m ON od.item_id = m.item_id
            WHERE od.order_id = ?
        """, (order['order_id'],))
        order['items'] = [dict(row) for row in cursor.fetchall()]
        
    conn.close()
    return orders

def get_all_orders():
    """Retrieves all orders (for Admin)."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT o.*, u.username 
        FROM Orders o
        JOIN Users u ON o.user_id = u.user_id
        ORDER BY o.timestamp DESC
    """)
    orders = [dict(row) for row in cursor.fetchall()]
    
    for order in orders:
        cursor.execute("""
            SELECT od.quantity, m.name 
            FROM OrderDetails od
            JOIN MenuItems m ON od.item_id = m.item_id
            WHERE od.order_id = ?
        """, (order['order_id'],))
        order['items'] = [dict(row) for row in cursor.fetchall()]
        
    conn.close()
    return orders

def update_order_status(order_id, new_status):
    """Updates the status of an order."""
    if new_status not in ['Pending', 'Preparing', 'Ready', 'Collected']:
        return False, "Invalid status."
        
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE Orders SET status = ? WHERE order_id = ?", (new_status, order_id))
        conn.commit()
        return True, "Status updated."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()
