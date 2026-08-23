"""
Адаптер для ВКонтакте.
Использует Long Poll API для получения сообщений.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id

from core.shop_bot import ShopBot
from core.database import init_db
from dotenv import load_dotenv

load_dotenv()


class VKAdapter:
    """
    Адаптер для ВКонтакте.
    
    Получает сообщения через Long Poll API, передаёт их в ядро,
    и отправляет ответы обратно пользователю с клавиатурами.
    """
    
    def __init__(self, token: str, group_id: int):
        self.token = token
        self.group_id = group_id
        self.bot = ShopBot()
        init_db()
    
    def run(self):
        """Запускает бота для ВКонтакте."""
        print("🚀 Запуск VK адаптера для E-Commerce Bot Core...")
        
        # Авторизация
        vk_session = VkApi(token=self.token)
        vk = vk_session.get_api()
        longpoll = VkBotLongPoll(vk_session, self.group_id)
        
        print("✅ Бот запущен и слушает сообщения...")
        
        try:
            for event in longpoll.listen():
                if event.type == VkBotEventType.MESSAGE_NEW:
                    self._handle_message(vk, event)
                elif event.type == VkBotEventType.MESSAGE_EVENT:
                    self._handle_callback(vk, event)
        
        except KeyboardInterrupt:
            print("\n🛑 Бот остановлен")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    def _handle_message(self, vk, event):
        """Обрабатывает текстовые сообщения"""
        message = event.object.message
        user_id = message["from_id"]
        text = message.get("text", "").strip()
        
        if not text:
            return
        
        print(f"📩 Сообщение от {user_id}: {text}")
        
        # Передаём в ядро
        reply, keyboard_data = self.bot.handle_message(user_id, text)
        
        # Отправляем ответ
        keyboard = self._build_keyboard(keyboard_data)
        vk.messages.send(
            user_id=user_id,
            message=reply,
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard() if keyboard else None
        )
    
    def _handle_callback(self, vk, event):
        """Обрабатывает нажатия на кнопки (для будущих улучшений)"""
        user_id = event.object.user_id
        payload = event.object.payload
        
        print(f"🔘 Callback от {user_id}: {payload}")
        
        # Отвечаем на callback (убираем "часики" на кнопке)
        vk.messages.sendMessageEventAnswer(
            event_id=event.object.event_id,
            user_id=user_id,
            peer_id=event.object.peer_id
        )
        
        # Здесь можно добавить обработку кнопок через ядро
        # Например, выбор товара из каталога
        if payload.get('action') == 'add_product':
            product_id = payload.get('product_id')
            reply, _ = self.bot.handle_message(user_id, f"/add_{product_id}")
            vk.messages.send(
                user_id=user_id,
                message=reply,
                random_id=get_random_id()
            )
    
    def _build_keyboard(self, keyboard_data):
        """
        Строит клавиатуру VK на основе данных от ядра.
        
        Args:
            keyboard_data: словарь с данными для клавиатуры
                Например: {"type": "catalog", "products": [...]}
        
        Returns:
            VkKeyboard или None
        """
        if not keyboard_data:
            return None
        
        keyboard = VkKeyboard(one_time=False, inline=True)
        
        if keyboard_data.get('type') == 'catalog':
            # Клавиатура с товарами (для быстрого добавления в корзину)
            for product in keyboard_data.get('products', []):
                label = f"➕ {product['name']} ({product['price']} ₽)"
                # Обрезаем до 40 символов (лимит VK)
                if len(label) > 40:
                    label = label[:37] + "..."
                keyboard.add_callback_button(
                    label=label,
                    color=VkKeyboardColor.PRIMARY,
                    payload={'action': 'add_product', 'product_id': product['id']}
                )
                keyboard.add_line()
        
        # Главная кнопка "Меню"
        keyboard.add_callback_button(
            label="🏠 Меню",
            color=VkKeyboardColor.SECONDARY,
            payload={'action': 'show_menu'}
        )
        
        return keyboard


if __name__ == "__main__":
    # Запуск адаптера
    token = os.getenv("VK_TOKEN")
    group_id = os.getenv("VK_GROUP_ID")
    
    if not token or not group_id:
        print("❌ Ошибка: VK_TOKEN и VK_GROUP_ID должны быть в .env")
        print("VK_TOKEN=ваш_токен")
        print("VK_GROUP_ID=123456789")
    else:
        adapter = VKAdapter(token, int(group_id))
        adapter.run()