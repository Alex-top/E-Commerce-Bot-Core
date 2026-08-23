import sqlite3

DB_PATH = "storage/db.sqlite"

def get_connection():
    """Возвращает соединение с базой данных."""
    return sqlite3.connect(DB_PATH)

def init_db():
    """Создаёт таблицы, если их нет."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Таблица товаров
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price INTEGER NOT NULL,
                description TEXT,
                stock INTEGER DEFAULT 0,
                image_url TEXT
            )
        """)
        
        # Таблица корзины (user_id -> товары)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cart (
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1,
                PRIMARY KEY (user_id, product_id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        """)
        
        # Таблица заказов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                items TEXT NOT NULL,
                total INTEGER NOT NULL,
                status TEXT DEFAULT 'новый',
                name TEXT,
                phone TEXT,
                address TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        print("✅ Таблицы созданы (или уже существуют)")