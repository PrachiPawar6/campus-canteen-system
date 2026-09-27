import streamlit as st
from database import init_db
from models.user import authenticate_user, register_user
from models.menu import get_all_menu_items, add_menu_item, update_menu_item, delete_menu_item
from models.order import place_order, get_orders_by_user, get_all_orders, update_order_status

# Initialize DB to ensure it exists
init_db()

st.set_page_config(page_title="Campus Canteen System", page_icon="🍔", layout="wide")

# Initialize Session State
if 'user' not in st.session_state:
    st.session_state.user = None
if 'cart' not in st.session_state:
    st.session_state.cart = {}

def login_register_page():
    st.title("🍔 Campus Canteen System")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login to your account")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                user = authenticate_user(username, password)
                if user:
                    st.session_state.user = user
                    st.success(f"Welcome back, {username}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
                    
    with tab2:
        st.subheader("Create a new student account")
        with st.form("register_form"):
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
            register_submit = st.form_submit_button("Register")
            
            if register_submit:
                if new_username and new_password:
                    success, msg = register_user(new_username, new_password, "student")
                    if success:
                        st.success("Registration successful! Please login from the Login tab.")
                    else:
                        st.error(msg)
                else:
                    st.error("Please fill in all fields.")

def student_dashboard():
    st.sidebar.title(f"Hello, {st.session_state.user['username']}")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.cart = {}
        st.rerun()
        
    st.title("Student Dashboard")
    
    tab_menu, tab_cart, tab_orders = st.tabs(["📋 Menu", "🛒 Cart", "📦 My Orders"])
    
    with tab_menu:
        st.subheader("Menu Items")
        items = get_all_menu_items(available_only=True)
        
        if not items:
            st.info("Menu is currently empty.")
        
        for item in items:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{item['name']}** ({item['category']})")
                    st.caption(item['description'])
                with col2:
                    st.markdown(f"**₹{item['price']}**")
                with col3:
                    if st.button("Add to Cart", key=f"add_{item['item_id']}"):
                        if item['item_id'] in st.session_state.cart:
                            st.session_state.cart[item['item_id']]['quantity'] += 1
                        else:
                            st.session_state.cart[item['item_id']] = {
                                'item_id': item['item_id'],
                                'name': item['name'],
                                'price': item['price'],
                                'quantity': 1
                            }
                        st.success(f"Added {item['name']} to cart!")
                st.divider()

    with tab_cart:
        st.subheader("Your Cart")
        if not st.session_state.cart:
            st.info("Your cart is empty.")
        else:
            total = 0
            for item_id, cart_item in list(st.session_state.cart.items()):
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                with col1:
                    st.write(cart_item['name'])
                with col2:
                    st.write(f"₹{cart_item['price']}")
                with col3:
                    st.write(f"Qty: {cart_item['quantity']}")
                with col4:
                    if st.button("Remove", key=f"rem_{item_id}"):
                        del st.session_state.cart[item_id]
                        st.rerun()
                total += cart_item['price'] * cart_item['quantity']
                
            st.write("---")
            st.markdown(f"### Total: ₹{total}")
            
            if st.button("Place Order"):
                cart_list = list(st.session_state.cart.values())
                success, result = place_order(st.session_state.user['user_id'], cart_list)
                if success:
                    st.success(f"Order placed successfully! Your Token Number is: **{result}**")
                    st.session_state.cart = {}
                else:
                    st.error(result)

    with tab_orders:
        st.subheader("Order History")
        orders = get_orders_by_user(st.session_state.user['user_id'])
        if not orders:
            st.info("You haven't placed any orders yet.")
        else:
            for order in orders:
                with st.expander(f"Order #{order['order_id']} - Token: {order['token_number']} - {order['status']}"):
                    st.write(f"**Date:** {order['timestamp']}")
                    st.write(f"**Total Amount:** ₹{order['total_amount']}")
                    st.write("**Items:**")
                    for item in order['items']:
                        st.write(f"- {item['name']} (x{item['quantity']}) : ₹{item['price_at_order']} each")

def admin_dashboard():
    st.sidebar.title("Admin Panel")
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.cart = {}
        st.rerun()
        
    st.title("Admin Dashboard")
    
    tab_orders, tab_menu = st.tabs(["Manage Orders", "Manage Menu"])
    
    with tab_orders:
        st.subheader("All Orders")
        orders = get_all_orders()
        if not orders:
            st.info("No orders found.")
        else:
            for order in orders:
                with st.expander(f"Order #{order['order_id']} | User: {order['username']} | Status: {order['status']}"):
                    st.write(f"**Token:** {order['token_number']}")
                    st.write(f"**Total Amount:** ₹{order['total_amount']}")
                    st.write(f"**Date:** {order['timestamp']}")
                    
                    st.write("**Items:**")
                    for item in order['items']:
                        st.write(f"- {item['name']} (x{item['quantity']})")
                        
                    # Update status
                    new_status = st.selectbox(
                        "Update Status", 
                        ['Pending', 'Preparing', 'Ready', 'Collected'],
                        index=['Pending', 'Preparing', 'Ready', 'Collected'].index(order['status']),
                        key=f"status_{order['order_id']}"
                    )
                    
                    if st.button("Save Status", key=f"btn_status_{order['order_id']}"):
                        success, msg = update_order_status(order['order_id'], new_status)
                        if success:
                            st.success(f"Status updated to {new_status}")
                            st.rerun()
                        else:
                            st.error(msg)
                            
    with tab_menu:
        st.subheader("Menu Management")
        
        # Add new item
        with st.expander("Add New Menu Item"):
            with st.form("add_menu_form"):
                name = st.text_input("Name")
                category = st.selectbox("Category", ["Snacks", "Meals", "Beverages", "Bakery", "Other"])
                description = st.text_area("Description")
                price = st.number_input("Price (₹)", min_value=0.0, step=1.0)
                is_available = st.checkbox("Available", value=True)
                
                if st.form_submit_button("Add Item"):
                    if name and price > 0:
                        success, msg = add_menu_item(name, description, price, category, is_available)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.error("Please enter a valid name and price.")
                        
        st.write("---")
        st.subheader("Existing Items")
        items = get_all_menu_items(available_only=False)
        for item in items:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{item['name']}** - {item['category']}")
                status = "Available" if item['is_available'] else "Unavailable"
                st.caption(f"₹{item['price']} | {status}")
            with col2:
                # Toggle Availability
                new_avail = not item['is_available']
                btn_text = "Make Unavailable" if item['is_available'] else "Make Available"
                if st.button(btn_text, key=f"avail_{item['item_id']}"):
                    update_menu_item(item['item_id'], item['name'], item['description'], item['price'], item['category'], new_avail)
                    st.rerun()
            with col3:
                # Delete
                if st.button("Delete", key=f"del_{item['item_id']}"):
                    success, msg = delete_menu_item(item['item_id'])
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            st.divider()

# Main Logic
if not st.session_state.user:
    login_register_page()
else:
    if st.session_state.user['role'] == 'admin':
        admin_dashboard()
    else:
        student_dashboard()
