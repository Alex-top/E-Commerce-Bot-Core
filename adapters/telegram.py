
"""
Адаптер для Telegram.
Для тестирования потребуется VPN или запуск на сервере.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.shop_bot import ShopBot
from core.database import init_db

# Заглушка, если библиотека не установлена
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("⚠️ Библиотека python-telegram-bot не установлена. Установите: pip install python-telegram-bot")

class TelegramAdapter:
    """
    Адаптер для Telegram.
    
    Для работы с Telegram в РФ требуется VPN или запуск на сервере за пределами РФ.
    """
    
    def __init__(self, token: str):
        if not TELEGRAM_AVAILABLE:
            raise ImportError("Установите python-telegram-bot: pip install python-telegram-bot")
        
        self.token = token
        self.bot = ShopBot()
        init_db()
    
    def run(self):
        """Запускает бота."""
        app = Application.builder().token(self.token).build()
        
        # Команды
        app.add_handler(CommandHandler("start", self._handle_start))
        app.add_handler(CommandHandler("catalog", self._handle_catalog))
        app.add_handler(CommandHandler("cart", self._handle_cart))
        app.add_handler(CommandHandler("checkout", self._handle_checkout))
        app.add_handler(CommandHandler("orders", self._handle_orders))
        app.add_handler(CommandHandler("clear_cart", self._handle_clear_cart))
        app.add_handler(CommandHandler("help", self._handle_help))
        
        # Добавляем обработчик текстовых сообщений (для команд вида /add_1)
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_text))
        
        print("🚀 Telegram бот запущен. Нажмите Ctrl+C для остановки.")
        app.run_polling()
    
    async def _handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        reply, _ = self.bot.handle_message(update.effective_user.id, "/start")
        await update.message.reply_text(reply)
    
    async def _handle_catalog(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        reply, _ = self.bot.handle_message(update.effective_user.id, "/catalog")
        await update.message.reply_text(reply)
    
    async def _handle_cart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        reply, _ = self.bot.handle_message(update.effective_user.id, "/cart")
        await update.message.reply_text(reply)
    
    async def _handle_checkout(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        reply, _ = self.bot.handle_message(update.effective_user.id, "/checkout")
        await update.message.reply_text(reply)
    
    async def _handle_orders(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        reply, _ = self.bot.handle_message(update.effective_user.id, "/orders")
        await update.message.reply_text(reply)
    
    async def _handle_clear_cart(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        reply, _ = self.bot.handle_message(update.effective_user.id, "/clear_cart")
        await update.message.reply_text(reply)
    
    async def _handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """📖 *Доступные команды:*

/catalog — каталог товаров
/add_N — добавить товар N в корзину
/cart — показать корзину
/set_N_M — установить количество товара N = M
/clear_cart — очистить корзину
/checkout — оформить заказ
/orders — мои заказы
/help — эта справка"""
        await update.message.reply_text(help_text)
    
    async def _handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обрабатывает текстовые команды вида /add_1, /set_1_3 и т.д."""
        text = update.message.text.strip()
        if text.startswith("/"):
            reply, _ = self.bot.handle_message(update.effective_user.id, text)
            await update.message.reply_text(reply)

if __name__ == "__main__":
    # Для запуска адаптера нужно указать токен бота в .env
    from dotenv import load_dotenv
    load_dotenv()
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ Ошибка: TELEGRAM_BOT_TOKEN не найден в .env")
        print("Создайте бота через @BotFather и добавьте токен в .env:")
        print("TELEGRAM_BOT_TOKEN=ваш_токен")
    else:
        adapter = TelegramAdapter(token)
        adapter.run()