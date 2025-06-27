import random
import time
import datetime
import pytz
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Customer, Employee, MenuItem, Order, OrderItem, Inventory, AccountBalance

# Set up database
engine = create_engine('sqlite:///coffee_shop.db')
Session = sessionmaker(bind=engine)

# Business hours
OPEN_HOUR = 7
CLOSE_HOUR = 19
TIMEZONE = pytz.timezone('US/Eastern')

# Payment methods
PAYMENT_METHODS = ['cash', 'card', 'mobile']

def is_business_open(now=None):
    now = now or datetime.datetime.now(TIMEZONE)
    return OPEN_HOUR <= now.hour < CLOSE_HOUR

def simulate_transaction():
    session = Session()
    # Get random customer (or None for walk-in)
    customers = session.query(Customer).all()
    customer = random.choice(customers) if customers and random.random() > 0.2 else None
    # Get random employee
    employees = session.query(Employee).all()
    employee = random.choice(employees) if employees else None
    # Get random menu items (1-3 per order)
    menu_items = session.query(MenuItem).filter_by(is_active=True).all()
    num_items = random.randint(1, 3)
    items = random.sample(menu_items, num_items)
    # Create order
    order = Order(
        customer_id=customer.id if customer else None,
        employee_id=employee.id if employee else None,
        order_time=datetime.datetime.now(TIMEZONE),
        total_amount=0.0,
        payment_method=random.choice(PAYMENT_METHODS)
    )
    session.add(order)
    session.flush()  # Get order.id
    total = 0.0
    for item in items:
        quantity = random.randint(1, 3)
        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=item.id,
            quantity=quantity,
            item_price=item.price
        )
        session.add(order_item)
        total += item.price * quantity
        # Update inventory (if tracked)
        inv = session.query(Inventory).filter(Inventory.item_name.ilike(f'%{item.name}%')).first()
        if inv:
            inv.quantity_on_hand = max(0, inv.quantity_on_hand - quantity)
    order.total_amount = round(total, 2)
    # Update account balance
    account = session.query(AccountBalance).order_by(AccountBalance.date.desc()).first()
    if account:
        account.balance += order.total_amount
    session.commit()
    order_id = order.id
    order_time = order.order_time

    # Reorder inventory if needed
    for inv in session.query(Inventory).all():
        if inv.quantity_on_hand <= inv.reorder_level:
            # Determine average price per unit (use MenuItem cost if available, else $2/unit)
            menu_item = session.query(MenuItem).filter_by(name=inv.item_name.rstrip('s')).first()
            avg_price = menu_item.cost if menu_item else 2.0
            restock_qty = 20
            reorder_amount = restock_qty - inv.quantity_on_hand
            if reorder_amount > 0:
                inv.quantity_on_hand = restock_qty
                reorder_cost = reorder_amount * avg_price
                account = session.query(AccountBalance).order_by(AccountBalance.date.desc()).first()
                if account:
                    account.balance -= reorder_cost
                session.commit()
                print(f"Reordered {reorder_amount} {inv.item_name} at ${avg_price:.2f}/unit. Total cost: ${reorder_cost:.2f}")
                with open('reorder_log.txt', 'a') as logf:
                    logf.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Reordered {reorder_amount} {inv.item_name} at ${avg_price:.2f}/unit. Total cost: ${reorder_cost:.2f}\n")

    session.close()
    print(f"Added order {order_id} at {order_time.strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    print('Starting transaction simulation...')
    while True:
        now = datetime.datetime.now(TIMEZONE)
        if is_business_open(now):
            simulate_transaction()
            time.sleep(random.randint(10, 30))  # Wait 10-30 seconds between transactions
        else:
            print('Business is closed. Waiting for opening hour...')
            # Sleep until next open hour
            tomorrow = now + datetime.timedelta(days=1)
            next_open = now.replace(hour=OPEN_HOUR, minute=0, second=0, microsecond=0)
            if now.hour >= CLOSE_HOUR:
                next_open = tomorrow.replace(hour=OPEN_HOUR, minute=0, second=0, microsecond=0)
            sleep_seconds = (next_open - now).total_seconds()
            time.sleep(max(60, sleep_seconds))

if __name__ == '__main__':
    main() 