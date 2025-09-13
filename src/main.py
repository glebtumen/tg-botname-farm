import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.ext._utils.types import HandlerCallback
from telegram.error import RetryAfter
import asyncio

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

SALE_MESSAGE = "🤖 Данный телеграм-бот находится на продаже. 🛒\n\nДля приобретения обратитесь к @wlzeusgod\n\n\nBot is on sale: @wlzeusgod"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    try:
        await update.message.reply_text(SALE_MESSAGE)
    except RetryAfter as e:
        # Обработка rate limit
        logger.warning(f"Rate limit exceeded, retrying after {e.retry_after} seconds")
        await asyncio.sleep(e.retry_after)
        await update.message.reply_text(SALE_MESSAGE)

async def handle_other_commands(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик всех остальных команд"""
    if update.message and update.message.text and update.message.text.startswith('/'):
        # Отвечаем только на команды (сообщения, начинающиеся с /)
        await update.message.reply_text(SALE_MESSAGE)

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений (не команд)"""
    if update.message and update.message.text and not update.message.text.startswith('/'):
        # Можно либо игнорировать, либо тоже отвечать
        await update.message.reply_text(SALE_MESSAGE)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    # Получаем токен из переменных окружения (рекомендуется)
    # token = os.getenv('BOT_TOKEN')
    # Или напрямую (только для теста)
    token = os.getenv('BOT_TOKEN')

    # Создаем приложение с настройками rate limiting
    app = ApplicationBuilder().token(token).build()
    
    # Добавляем обработчики
    app.add_handler(CommandHandler("start", start))
    
    # Обработчик всех остальных команд
    app.add_handler(MessageHandler(filters.COMMAND & ~filters.Command("start"), handle_other_commands))
    
    # Обработчик текстовых сообщений (опционально - можно убрать если хотите игнорировать)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    
    # Добавляем обработчик ошибок
    app.add_error_handler(error_handler)
    
    logger.info("Bot is starting...")
    app.run_polling(
        drop_pending_updates=True,  # Игнорируем накопившиеся апдейты при старте
        allowed_updates=['message', 'edited_message']  # Обрабатываем только сообщения
    )

if __name__ == '__main__':
    main()