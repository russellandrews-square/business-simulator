import streamlit as st
from streamlit_autorefresh import st_autorefresh
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Customer, Employee, MenuItem, Inventory, AccountBalance, Order, Base
import pandas as pd
import time
import urllib.parse
import os

# Auto-refresh every 10 seconds
st_autorefresh(interval=10 * 1000, key="datarefresh")

# Database setup
@st.cache_resource
def init_database():
    engine = create_engine('sqlite:///coffee_shop.db')
    
    # Create tables if they don't exist
    Base.metadata.create_all(engine)
    
    # Check if database is empty and seed it
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # If no customers exist, seed the database
    if session.query(Customer).count() == 0:
        from seed_db import seed_database
        seed_database()
    
    session.close()
    return engine

engine = init_database()
Session = sessionmaker(bind=engine)
session = Session()

# Sidebar navigation
st.sidebar.title('Navigation')
page = st.sidebar.radio(
    'Go to',
    ('Home', 'Customers', 'Employees', 'Menu Items', 'Inventory', 'Account Balance', 'Transactions/Orders')
)

st.title('Coffee Shop Dashboard')

if page == 'Home':
    st.header('Overview')
    # Basic stats
    num_customers = session.query(Customer).count()
    num_employees = session.query(Employee).count()
    num_menu_items = session.query(MenuItem).count()
    account_balance = session.query(AccountBalance).order_by(AccountBalance.date.desc()).first()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric('Customers', num_customers)
    col2.metric('Employees', num_employees)
    col3.metric('Menu Items', num_menu_items)
    col4.metric('Account Balance', f"${account_balance.balance:,.2f}" if account_balance else 'N/A')

    # Inventory levels chart
    st.subheader('Inventory Levels')
    inventory = session.query(Inventory).all()
    if inventory:
        df_inventory = pd.DataFrame([
            {
                'Item': item.item_name,
                'Quantity': item.quantity_on_hand,
                'Unit': item.unit
            } for item in inventory
        ])
        st.bar_chart(df_inventory.set_index('Item')['Quantity'])
    else:
        st.write('No inventory data available.')

    # Recent customers
    st.subheader('Recent Customers')
    recent_customers = session.query(Customer).order_by(Customer.created_at.desc()).limit(5).all()
    if recent_customers:
        df_customers = pd.DataFrame([
            {
                'Name': c.name,
                'Email': c.email,
                'Phone': c.phone,
                'Loyalty Points': c.loyalty_points,
                'Joined': c.created_at.strftime('%Y-%m-%d')
            } for c in recent_customers
        ])
        st.table(df_customers)
    else:
        st.write('No customer data available.')

    # Recent orders
    st.subheader('Recent Orders')
    recent_orders = session.query(Order).order_by(Order.order_time.desc()).limit(5).all()
    if recent_orders:
        df_orders = pd.DataFrame([
            {
                'Order Time': o.order_time.strftime('%Y-%m-%d %H:%M:%S'),
                'Customer': (session.get(Customer, o.customer_id).name if o.customer_id else 'Walk-in'),
                'Employee': (session.get(Employee, o.employee_id).name if o.employee_id else 'N/A'),
                'Total ($)': o.total_amount,
                'Payment': o.payment_method
            } for o in recent_orders
        ])
        st.table(df_orders)
    else:
        st.write('No orders yet.')

    # Recent inventory reorder events
    st.subheader('Recent Inventory Reorders')
    try:
        if os.path.exists('reorder_log.txt'):
            with open('reorder_log.txt', 'r') as f:
                reorder_lines = f.readlines()[-10:]
            if reorder_lines:
                for line in reorder_lines:
                    st.text(line.strip())
            else:
                st.write('No recent reorder events.')
        else:
            st.write('No reorder log found.')
    except Exception as e:
        st.write('Unable to read reorder log.')

elif page == 'Customers':
    st.header('Customers')
    customers = session.query(Customer).order_by(Customer.created_at.desc()).all()
    if customers:
        df = pd.DataFrame([
            {
                'Name': c.name,
                'Email': c.email,
                'Phone': c.phone,
                'Loyalty Points': c.loyalty_points,
                'Joined': c.created_at.strftime('%Y-%m-%d')
            } for c in customers
        ])
        st.table(df)
    else:
        st.write('No customer data available.')

elif page == 'Employees':
    st.header('Employees')
    employees = session.query(Employee).order_by(Employee.name).all()
    if employees:
        df = pd.DataFrame([
            {
                'Name': e.name,
                'Role': e.role,
                'Hourly Wage': e.hourly_wage,
                'Hire Date': e.hire_date.strftime('%Y-%m-%d')
            } for e in employees
        ])
        st.table(df)
    else:
        st.write('No employee data available.')

elif page == 'Menu Items':
    st.header('Menu Items')
    menu_items = session.query(MenuItem).order_by(MenuItem.category, MenuItem.name).all()
    if menu_items:
        df = pd.DataFrame([
            {
                'Name': m.name,
                'Category': m.category,
                'Price': m.price,
                'Cost': m.cost,
                'Active': m.is_active
            } for m in menu_items
        ])
        st.table(df)
    else:
        st.write('No menu items available.')

elif page == 'Inventory':
    st.header('Inventory')
    inventory = session.query(Inventory).order_by(Inventory.item_name).all()
    if inventory:
        df = pd.DataFrame([
            {
                'Item': i.item_name,
                'Quantity': i.quantity_on_hand,
                'Unit': i.unit,
                'Reorder Level': i.reorder_level
            } for i in inventory
        ])
        st.table(df)
    else:
        st.write('No inventory data available.')

elif page == 'Account Balance':
    st.header('Account Balance')
    balances = session.query(AccountBalance).order_by(AccountBalance.date.desc()).all()
    if balances:
        df = pd.DataFrame([
            {
                'Date': b.date.strftime('%Y-%m-%d'),
                'Balance': b.balance,
                'Notes': b.notes
            } for b in balances
        ])
        st.table(df)
    else:
        st.write('No account balance data available.')

elif page == 'Transactions/Orders':
    st.header('Transactions / Orders')
    orders = session.query(Order).order_by(Order.order_time.desc()).all()
    if orders:
        # Use query params to track selected order
        query_params = st.query_params
        selected_order_id = int(query_params.get('order_id', [0])[0]) if 'order_id' in query_params else None

        # Build table with clickable order numbers
        table_rows = []
        for o in orders:
            order_link = f"[#{o.id}](?order_id={o.id})"
            table_rows.append({
                'Order': order_link,
                'Order Time': o.order_time.strftime('%Y-%m-%d %H:%M:%S'),
                'Customer': (session.get(Customer, o.customer_id).name if o.customer_id else 'Walk-in'),
                'Employee': (session.get(Employee, o.employee_id).name if o.employee_id else 'N/A'),
                'Total ($)': o.total_amount,
                'Payment': o.payment_method
            })
        df = pd.DataFrame(table_rows)
        st.markdown(df.to_markdown(index=False), unsafe_allow_html=True)

        # Show receipt if an order is selected
        if selected_order_id:
            selected_order = session.get(Order, selected_order_id)
            if selected_order:
                st.subheader(f'Receipt for Order #{selected_order.id}')
                st.markdown(f"**Order Time:** {selected_order.order_time.strftime('%Y-%m-%d %H:%M:%S')}")
                st.markdown(f"**Customer:** {session.get(Customer, selected_order.customer_id).name if selected_order.customer_id else 'Walk-in'}")
                st.markdown(f"**Employee:** {session.get(Employee, selected_order.employee_id).name if selected_order.employee_id else 'N/A'}")
                st.markdown(f"**Payment Method:** {selected_order.payment_method}")
                st.markdown(f"**Total:** ${selected_order.total_amount:.2f}")
                st.markdown('**Items:**')
                items = [
                    {
                        'Item': session.get(MenuItem, oi.menu_item_id).name,
                        'Quantity': oi.quantity,
                        'Price': oi.item_price,
                        'Subtotal': oi.quantity * oi.item_price
                    } for oi in selected_order.order_items
                ]
                df_items = pd.DataFrame(items)
                st.table(df_items)
    else:
        st.write('No orders yet.') 