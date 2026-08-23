import sys
import os

# Добавляем путь к корню проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.shop_bot import ShopBot
from core.database import init_db
from scripts.seed import seed_products

def main():
    print("🛒 Запуск E-Commerce Bot Core в консольном режиме")
    print("=" * 50)
    
    # Инициализация БД и тестовых данных
    init_db()
    seed_products()
    
    bot = ShopBot()
    user_id = 1  # Тестовый пользователь
    
    print("\n👋 Доступные команды:")
    print("  /start - главное меню")
    print("  /catalog - каталог товаров")
    print("  /add_N - добавить товар N в корзину")
    print("  /cart - показать корзину")
    print("  /set_N_M - установить количество товара N = M")
    print("  /clear_cart - очистить корзину")
    print("  /checkout - оформить заказ")
    print("  /orders - мои заказы")
    print("  /exit - выход")
    print("=" * 50)
    
    while True:
        text = input("\n👤 Вы: ").strip()
        if text.lower() == "/exit":
            print("👋 До свидания!")
            break
        
        reply, _ = bot.handle_message(user_id, text)
        print(f"🤖 Бот: {reply}")

if __name__ == "__main__":
    main()