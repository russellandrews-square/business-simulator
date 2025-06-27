from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Date, Time
from sqlalchemy.orm import declarative_base, relationship
import datetime

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True)
    phone = Column(String, unique=True)
    loyalty_points = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    orders = relationship('Order', back_populates='customer')

class Employee(Base):
    __tablename__ = 'employees'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    hourly_wage = Column(Float, nullable=False)
    hire_date = Column(Date, default=datetime.date.today)
    schedules = relationship('StaffSchedule', back_populates='employee')
    orders = relationship('Order', back_populates='employee')

class StaffSchedule(Base):
    __tablename__ = 'staff_schedules'
    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    shift_date = Column(Date, nullable=False)
    shift_start = Column(Time, nullable=False)
    shift_end = Column(Time, nullable=False)
    employee = relationship('Employee', back_populates='schedules')

class MenuItem(Base):
    __tablename__ = 'menu_items'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    order_items = relationship('OrderItem', back_populates='menu_item')

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    order_time = Column(DateTime, default=datetime.datetime.utcnow)
    total_amount = Column(Float, nullable=False)
    payment_method = Column(String, nullable=False)
    customer = relationship('Customer', back_populates='orders')
    employee = relationship('Employee', back_populates='orders')
    order_items = relationship('OrderItem', back_populates='order')

class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    menu_item_id = Column(Integer, ForeignKey('menu_items.id'))
    quantity = Column(Integer, nullable=False)
    item_price = Column(Float, nullable=False)
    order = relationship('Order', back_populates='order_items')
    menu_item = relationship('MenuItem', back_populates='order_items')

class Inventory(Base):
    __tablename__ = 'inventory'
    id = Column(Integer, primary_key=True)
    item_name = Column(String, nullable=False)
    quantity_on_hand = Column(Float, nullable=False)
    reorder_level = Column(Float, nullable=False)
    unit = Column(String, nullable=False)

class AccountBalance(Base):
    __tablename__ = 'account_balance'
    id = Column(Integer, primary_key=True)
    date = Column(Date, default=datetime.date.today)
    balance = Column(Float, nullable=False)
    notes = Column(String) 