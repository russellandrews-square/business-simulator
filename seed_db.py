from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Customer, Employee, StaffSchedule, MenuItem, Inventory, AccountBalance
from faker import Faker
import random
import datetime

def seed_database():
    """Seed the database with sample data"""
    engine = create_engine('sqlite:///coffee_shop.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    fake = Faker()

    # Seed Customers
    def seed_customers(n=30):
        customers = []
        for _ in range(n):
            customer = Customer(
                name=fake.name(),
                email=fake.unique.email(),
                phone=fake.unique.phone_number(),
                loyalty_points=random.randint(0, 200)
            )
            customers.append(customer)
        session.add_all(customers)
        session.commit()

    # Seed Employees
    def seed_employees():
        roles = ['Barista', 'Manager', 'Cashier']
        employees = []
        for role in roles:
            for _ in range(3 if role != 'Manager' else 1):
                employee = Employee(
                    name=fake.name(),
                    role=role,
                    hourly_wage=round(random.uniform(15, 25) if role != 'Manager' else 30, 2),
                    hire_date=fake.date_between(start_date='-2y', end_date='today')
                )
                employees.append(employee)
        session.add_all(employees)
        session.commit()

    # Seed Menu Items
    def seed_menu_items():
        items = [
            ('Espresso', 'Coffee', 3.0, 0.5),
            ('Latte', 'Coffee', 4.0, 0.7),
            ('Cappuccino', 'Coffee', 4.0, 0.7),
            ('Americano', 'Coffee', 3.5, 0.6),
            ('Mocha', 'Coffee', 4.5, 0.8),
            ('Tea', 'Tea', 2.5, 0.3),
            ('Hot Chocolate', 'Other', 3.5, 0.6),
            ('Croissant', 'Pastry', 3.0, 1.0),
            ('Muffin', 'Pastry', 2.5, 0.8),
            ('Bagel', 'Pastry', 2.0, 0.7),
        ]
        menu_items = [MenuItem(name=name, category=cat, price=price, cost=cost) for name, cat, price, cost in items]
        session.add_all(menu_items)
        session.commit()

    # Seed Inventory
    def seed_inventory():
        inventory_items = [
            ('Espresso Beans', 20, 5, 'kg'),
            ('Milk', 30, 10, 'L'),
            ('Tea Leaves', 10, 2, 'kg'),
            ('Chocolate Syrup', 5, 2, 'L'),
            ('Croissants', 15, 5, 'pcs'),
            ('Muffins', 15, 5, 'pcs'),
            ('Bagels', 15, 5, 'pcs'),
        ]
        inventory = [Inventory(item_name=name, quantity_on_hand=qty, reorder_level=reorder, unit=unit) for name, qty, reorder, unit in inventory_items]
        session.add_all(inventory)
        session.commit()

    # Seed Account Balance
    def seed_account_balance():
        balance = AccountBalance(
            date=datetime.date.today(),
            balance=round(random.uniform(1000, 5000), 2),
            notes='Initial seed balance.'
        )
        session.add(balance)
        session.commit()

    # Run all seeding functions
    seed_customers()
    seed_employees()
    seed_menu_items()
    seed_inventory()
    seed_account_balance()
    session.close()

if __name__ == '__main__':
    seed_database()
    print('Database seeded with sample data!') 