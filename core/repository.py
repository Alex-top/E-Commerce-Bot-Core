import json
import sqlite3
from typing import List, Optional, Dict, Any
from .database import get_connection
from .models import Product, CartItem, Order

class Repository:
    def __init__(self):
        pass
    
    # === ТОВАРЫ ===
    def get_all_products(self) -> List[Product]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, price, description, stock, image_url FROM products")
            rows = cursor.fetchall()
            return [Product(id=row[0], name=row[1], price=row[2], description=row[3], stock=row[4], image_url=row[5]) for row in rows]
    
    def get_product(self, product_id: int) -> Optional[Product]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, price, description, stock, image_url FROM products WHERE id=?", (product_id,))
            row = cursor.fetchone()
            if row:
                return Product(id=row[0], name=row[1], price=row[2], description=row[3], stock=row[4], image_url=row[5])
            return None
    
    # === КОРЗИНА ===
    def get_cart(self, user_id: int) -> List[CartItem]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT cart.product_id, cart.quantity, products.name, products.price 
                FROM cart 
                JOIN products ON cart.product_id = products.id 
                WHERE cart.user_id=?
            """, (user_id,))
            rows = cursor.fetchall()
            return [CartItem(product_id=row[0], quantity=row[1], product_name=row[2], product_price=row[3]) for row in rows]
    
    def add_to_cart(self, user_id: int, product_id: int, quantity: int = 1) -> bool:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO cart (user_id, product_id, quantity) 
                VALUES (?, ?, ?) 
                ON CONFLICT(user_id, product_id) DO UPDATE SET quantity = quantity + ?
            """, (user_id, product_id, quantity, quantity))
            conn.commit()
            return True
    
    def update_cart_quantity(self, user_id: int, product_id: int, quantity: int) -> bool:
        if quantity <= 0:
            return self.remove_from_cart(user_id, product_id)
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE cart SET quantity=? WHERE user_id=? AND product_id=?", (quantity, user_id, product_id))
            conn.commit()
            return True
    
    def remove_from_cart(self, user_id: int, product_id: int) -> bool:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cart WHERE user_id=? AND product_id=?", (user_id, product_id))
            conn.commit()
            return True
    
    def clear_cart(self, user_id: int) -> bool:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cart WHERE user_id=?", (user_id,))
            conn.commit()
            return True
    
    # === ЗАКАЗЫ ===
    def create_order(self, order: Order) -> int:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO orders (user_id, items, total, status, name, phone, address)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (order.user_id, json.dumps(order.items), order.total, order.status, order.name, order.phone, order.address))
            conn.commit()
            return cursor.lastrowid
    
    def get_user_orders(self, user_id: int) -> List[Order]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, user_id, items, total, status, name, phone, address, created_at FROM orders WHERE user_id=? ORDER BY created_at DESC", (user_id,))
            rows = cursor.fetchall()
            return [Order(id=row[0], user_id=row[1], items=json.loads(row[2]), total=row[3], status=row[4], name=row[5], phone=row[6], address=row[7], created_at=row[8]) for row in rows]