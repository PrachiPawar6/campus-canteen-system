import sqlite3
import os

DB_NAME = "canteen.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT CHECK(role IN ('student', 'admin')) NOT NULL
        )
    """)

    # 2. MenuItems table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS MenuItems (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            is_available INTEGER DEFAULT 1 CHECK(is_available IN (0, 1))
        )
    """)

    # 3. Orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total_amount REAL NOT NULL,
            status TEXT CHECK(status IN ('Pending', 'Preparing', 'Ready', 'Collected')) NOT NULL,
            token_number INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
    """)

    # 4. OrderDetails table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS OrderDetails (
            detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            price_at_order REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES Orders(order_id),
            FOREIGN KEY (item_id) REFERENCES MenuItems(item_id)
        )
    """)

    # Default Admin Account
    cursor.execute("SELECT COUNT(*) FROM Users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO Users (username, password, role) VALUES (?, ?, ?)",
            ("admin", "admin123", "admin")
        )

    # Check and insert menu items
    cursor.execute("SELECT COUNT(*) FROM MenuItems")
    count = cursor.fetchone()[0]

    if count == 0:
        sample_menu = [
            # Snacks & Quick Bites
            ("Samosa (2 pcs)", "Snacks", "Crispy spiced potato pastries served with mint chutney", 25.00, 1),
            ("Vada Pav", "Snacks", "Mumbai classic spiced potato fritter in a soft bun with chutneys", 20.00, 1),
            ("Veg Puff / Patty", "Snacks", "Flaky puff pastry stuffed with seasoned vegetables", 20.00, 1),
            ("French Fries", "Snacks", "Crispy salted golden potato fries with dip", 50.00, 1),
            ("Veg Cheese Sandwich", "Snacks", "Toasted sandwich loaded with veggies, cheese, and herb spread", 60.00, 1),
            ("Paneer Kathi Roll", "Snacks", "Warm paratha wrapped around spicy grilled paneer and onions", 80.00, 1),

            # South Indian / Breakfast
            ("Masala Dosa", "Meals", "Crisp rice crepe stuffed with spiced potato masala and sambar", 60.00, 1),
            ("Idli Sambhar (2 pcs)", "Meals", "Steamed rice cakes served with hot lentil sambar and coconut chutney", 40.00, 1),
            ("Medu Vada (2 pcs)", "Meals", "Crispy golden fried lentil donuts served with sambar", 45.00, 1),

            # Main Meals & Rice
            ("Veg Fried Rice", "Meals", "Wok-tossed basmati rice with crunchy seasonal veggies and soy sauce", 80.00, 1),
            ("Schezwan Noodles", "Meals", "Spicy stir-fried noodles with cabbage, carrots, and schezwan dip", 85.00, 1),
            ("Veg Biryani Combo", "Meals", "Aromatic basmati rice cooked with spices, served with raita and papad", 110.00, 1),
            ("Chole Bhature (2 pcs)", "Meals", "Spicy chickpea curry paired with deep-fried puffy bhature", 90.00, 1),
            ("Mini Thali", "Meals", "2 Rotis, Dal, Paneer subzi, Steamed Rice, and Pickle", 120.00, 1),

            # Beverages
            ("Masala Chai", "Beverages", "Freshly brewed Indian tea with cardamom and ginger", 15.00, 1),
            ("Filter Coffee", "Beverages", "Traditional South Indian frothy chicory-coffee blend", 25.00, 1),
            ("Cold Coffee", "Beverages", "Chilled whipped coffee topped with chocolate powder", 45.00, 1),
            ("Sweet Lassi", "Beverages", "Thick churned sweet yogurt flavored with cardamom and malai", 40.00, 1),
            ("Fresh Lemon Soda", "Beverages", "Refreshing sparkling lime soda (Sweet or Salted)", 30.00, 1),

            # Bakery & Desserts
            ("Chocolate Brownie", "Bakery", "Warm fudgy chocolate brownie square", 55.00, 1),
            ("Gulab Jamun (2 pcs)", "Bakery", "Soft milk-solid dumplings soaked in warm rose syrup", 35.00, 1),
            ("Butter Croissant", "Bakery", "Flaky, buttery baked crescent pastry", 50.00, 1)
        ]

        cursor.executemany("""
            INSERT INTO MenuItems (name, category, description, price, is_available)
            VALUES (?, ?, ?, ?, ?)
        """, sample_menu)

    conn.commit()
    conn.close()
    print("Database initialization complete.")

if __name__ == "__main__":
    init_db()