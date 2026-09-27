import sqlite3
from database import get_connection

def get_all_menu_items(available_only=False):
    from database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    
    if available_only:
        cursor.execute("SELECT item_id, name, category, description, price, is_available FROM MenuItems WHERE is_available = 1")
    else:
        cursor.execute("SELECT item_id, name, category, description, price, is_available FROM MenuItems")
        
    rows = cursor.fetchall()
    conn.close()

    items = []
    for r in rows:
        items.append({
            "item_id": r["item_id"] if isinstance(r, dict) or hasattr(r, 'keys') else r[0],
            "name": r["name"] if isinstance(r, dict) or hasattr(r, 'keys') else r[1],
            "category": r["category"] if isinstance(r, dict) or hasattr(r, 'keys') else r[2],
            "description": r["description"] if isinstance(r, dict) or hasattr(r, 'keys') else r[3],
            "price": float(r["price"] if isinstance(r, dict) or hasattr(r, 'keys') else r[4]),
            "is_available": r["is_available"] if isinstance(r, dict) or hasattr(r, 'keys') else r[5]
        })
    return items

def add_menu_item(name, description, price, category, is_available=True):
    """Adds a new menu item to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO MenuItems (name,price, description, category, is_available) VALUES (?, ?, ?, ?, ?)",
            (name, price, description, category, 1 if is_available else 0)
        )
        conn.commit()
        return True, "Menu item added successfully."
    except Exception as e:
        return False, f"An error occurred: {str(e)}"
    finally:
        conn.close()

def update_menu_item(item_id, name, description, price, category, is_available):
    """Updates an existing menu item."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE MenuItems 
            SET name = ?, description = ?, price = ?, category = ?, is_available = ?
            WHERE item_id = ?
        """, (name, description, price, category, 1 if is_available else 0, item_id))
        conn.commit()
        return True, "Menu item updated successfully."
    except Exception as e:
        return False, f"An error occurred: {str(e)}"
    finally:
        conn.close()

def delete_menu_item(item_id):
    """Deletes a menu item from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Before deleting, we should probably check if it's used in OrderDetails.
        # But SQLite with PRAGMA foreign_keys=ON will prevent deletion if it's referenced.
        # Alternatively, we can just catch the IntegrityError.
        cursor.execute("DELETE FROM MenuItems WHERE item_id = ?", (item_id,))
        conn.commit()
        return True, "Menu item deleted successfully."
    except sqlite3.IntegrityError:
        return False, "Cannot delete item: It is part of an existing order."
    except Exception as e:
        return False, f"An error occurred: {str(e)}"
    finally:
        conn.close()
