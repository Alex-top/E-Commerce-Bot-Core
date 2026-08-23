import sqlite3
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import get_connection, init_db

def seed_products():
    """Добавляет тестовые товары"""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Проверяем, есть ли уже товары
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] > 0:
            print("📦 Товары уже есть в базе, пропускаем добавление")
            return
        
        products = [
            ("Ноутбук Pro", 1500, "Мощный ноутбук для работы и игр", 10, ""),
            ("Мышь беспроводная", 25, "Тихая, удобная, с подсветкой", 50, ""),
            ("Клавиатура механическая", 80, "С подсветкой, для игр и работы", 30, ""),
            ("Монитор 27' 4K", 400, "Отличное качество для дизайна", 15, ""),
            ("Наушники Bluetooth", 120, "Шумоподавление, долгая работа", 20, ""),
        ]
        
        cursor.executemany("INSERT INTO products (name, price, description, stock, image_url) VALUES (?, ?, ?, ?, ?)", products)
        conn.commit()
        print(f"✅ Добавлено {len(products)} тестовых товаров")

if __name__ == "__main__":
    init_db()
    seed_products()
    print("🎉 База данных готова!")