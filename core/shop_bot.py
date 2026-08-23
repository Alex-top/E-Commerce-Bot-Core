from typing import Tuple, Optional, List, Dict, Any
from .repository import Repository
from .models import Order

class ShopBot:
    def __init__(self):
        self.repo = Repository()
        self.user_states = {}  # user_id -> текущий шаг
    
    def handle_message(self, user_id: int, text: str) -> Tuple[str, Optional[Dict]]:
        """Главный метод для обработки сообщения. Возвращает (ответ, клавиатура)"""
        text = text.strip().lower()
        
        if text == "/start":
            return self._show_main_menu()
        
        elif text == "/catalog":
            return self._show_catalog()
        
        elif text.startswith("/add_"):
            # /add_1 -> добавить товар с id=1
            try:
                product_id = int(text.split("_")[1])
                return self._add_to_cart(user_id, product_id)
            except:
                return "❌ Неверный формат. Используйте /add_1", None
        
        elif text == "/cart":
            return self._show_cart(user_id)
        
        elif text == "/clear_cart":
            return self._clear_cart(user_id)
        
        elif text == "/checkout":
            return self._start_checkout(user_id)
        
        elif text.startswith("/set_"):
            # /set_1_3 -> установить количество товара 1 = 3
            try:
                parts = text.split("_")
                product_id = int(parts[1])
                quantity = int(parts[2])
                return self._update_quantity(user_id, product_id, quantity)
            except:
                return "❌ Неверный формат. Используйте /set_1_3 (установить кол-во=3)", None
        
        elif text == "/orders":
            return self._show_orders(user_id)
        
        else:
            return "❓ Неизвестная команда. Доступные: /catalog, /cart, /checkout, /orders", None
    
    def _show_main_menu(self) -> Tuple[str, Optional[Dict]]:
        return "👋 Добро пожаловать в магазин!\n\n/catalog - посмотреть товары\n/cart - корзина\n/checkout - оформить заказ\n/orders - мои заказы", None
    
    def _show_catalog(self) -> Tuple[str, Optional[Dict]]:
        products = self.repo.get_all_products()
        if not products:
            return "😔 Товаров пока нет", None
        
        lines = ["📦 *Каталог товаров:*\n"]
        for p in products:
            lines.append(f"*{p.name}* — {p.price} ₽")
            if p.description:
                lines.append(f"  {p.description}")
            lines.append(f"  В наличии: {p.stock} шт.")
            lines.append(f"  /add_{p.id} — добавить в корзину\n")
        
        return "\n".join(lines), None
    
    def _add_to_cart(self, user_id: int, product_id: int) -> Tuple[str, Optional[Dict]]:
        product = self.repo.get_product(product_id)
        if not product:
            return "❌ Товар не найден", None
        if product.stock <= 0:
            return f"❌ Товар '{product.name}' закончился", None
        
        self.repo.add_to_cart(user_id, product_id)
        cart = self.repo.get_cart(user_id)
        total = sum(item.product_price * item.quantity for item in cart)
        return f"✅ {product.name} добавлен в корзину!\nВ корзине {len(cart)} товаров на {total} ₽", None
    
    def _show_cart(self, user_id: int) -> Tuple[str, Optional[Dict]]:
        cart = self.repo.get_cart(user_id)
        if not cart:
            return "🛒 Корзина пуста", None
        
        lines = ["🛒 *Ваша корзина:*\n"]
        for item in cart:
            lines.append(f"{item.product_name} x{item.quantity} = {item.product_price * item.quantity} ₽")
            lines.append(f"  /set_{item.product_id}_N — изменить количество")
            lines.append(f"  /remove_{item.product_id} — удалить")
        
        total = sum(item.product_price * item.quantity for item in cart)
        lines.append(f"\n💰 Итого: {total} ₽")
        lines.append("\n/checkout — оформить заказ")
        lines.append("/clear_cart — очистить корзину")
        
        return "\n".join(lines), None
    
    def _clear_cart(self, user_id: int) -> Tuple[str, Optional[Dict]]:
        self.repo.clear_cart(user_id)
        return "🛒 Корзина очищена", None
    
    def _update_quantity(self, user_id: int, product_id: int, quantity: int) -> Tuple[str, Optional[Dict]]:
        if quantity <= 0:
            self.repo.remove_from_cart(user_id, product_id)
            return "✅ Товар удалён из корзины", None
        self.repo.update_cart_quantity(user_id, product_id, quantity)
        return f"✅ Количество обновлено на {quantity}", None
    
    def _start_checkout(self, user_id: int) -> Tuple[str, Optional[Dict]]:
        cart = self.repo.get_cart(user_id)
        if not cart:
            return "🛒 Корзина пуста. Добавьте товары через /catalog", None
        
        # Простое оформление: собираем данные и создаём заказ
        items = [{"product_id": item.product_id, "quantity": item.quantity} for item in cart]
        total = sum(item.product_price * item.quantity for item in cart)
        
        order = Order(
            user_id=user_id,
            items=items,
            total=total,
            status="новый",
            name="Тестовый клиент",
            phone="+7 999 123-45-67",
            address="г. Москва, ул. Тестовая, д. 1"
        )
        
        order_id = self.repo.create_order(order)
        self.repo.clear_cart(user_id)
        
        return f"✅ Заказ #{order_id} оформлен!\nСумма: {total} ₽\nСпасибо за покупку!", None
    
    def _show_orders(self, user_id: int) -> Tuple[str, Optional[Dict]]:
        orders = self.repo.get_user_orders(user_id)
        if not orders:
            return "📭 У вас пока нет заказов", None
        
        lines = ["📋 *Ваши заказы:*\n"]
        for order in orders:
            lines.append(f"Заказ #{order.id} — {order.total} ₽")
            lines.append(f"  Статус: {order.status}")
            lines.append(f"  Дата: {order.created_at}\n")
        
        return "\n".join(lines), None