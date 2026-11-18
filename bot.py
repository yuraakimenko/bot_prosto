import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, ReplyKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    MessageHandler,
    Filters
)
from telegram.error import TelegramError
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Constants
SOCIAL_MEDIA = (
    "🧭 Наш сайт: http://prostogovorite\\.com\n"
    "📢 ТГ Канал: @prostogovoritech\n"
    "💬 Чат поддержки: @psysrb\n"
    "📸 Instagram: [@prostogovorite](https://instagram\\.com/prostogovorite)\n"
    "👥 Коммьюнити психологов в Сербии: [@psysrbcom](https://t.me/psysrbcom)\n\n"
)

RESPONSES = {
    'help': (
        "*Бесплатная психологическая помощь*\n\n"
        "До 10 сессий с проверенным специалистом\\. Подходит тем, кто испытывает финансовые трудности\\.\n\n"
        "→ Напишите координатору: @kondrashkin\\_pro\n\n"
        "*Также доступна поддержка от специально обученных волонтёров:*\n"
        "→ Написать: [@prostogovorite](https://t.me/prostogovoritech?direct)\n\n"
        "Помощь оказывается конфиденциально\n\n"
        "\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\n\n"
        "*Присоединяйтесь к Просто Говорить\\!*\n\n"
        "🧭 Наш сайт: http://prostogovorite\\.com\n"
        "📢 ТГ Канал: @prostogovoritech\n"
        "💬 Чат поддержки: @psysrb\n"
        "📸 Instagram: [@prostogovorite](https://instagram\\.com/prostogovorite)\n"
        "👥 Коммьюнити психологов в Сербии: [@psysrbcom](https://t\\.me/psysrbcom)"
    ),
    'find_psy': (
        "*Подбор психолога*\n\n"
        "Ищете специалиста, который подойдёт именно вам? "
        "Наш бот поможет подобрать психолога, учитывая ваш запрос, язык общения и другие важные параметры\\. "
        "Это конфиденциально\\.\n\n"
        "🤖 *Начать подбор через специализированного бота:*\n"
        "→ @PsyGovoritBOT\n\n"
        "🔍 *Также вы можете посмотреть каталог специалистов на нашем сайте:*\n"
        "→ prostogovorite\\.com\n\n"
        "\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\n\n"
        "*Присоединяйтесь к Просто Говорить\\!*\n\n"
        "🧭 Наш сайт: http://prostogovorite\\.com\n"
        "📢 ТГ Канал: @prostogovoritech\n"
        "💬 Чат поддержки: @psysrb\n"
        "📸 Instagram: [@prostogovorite](https://instagram\\.com/prostogovorite)\n"
        "👥 Коммьюнити психологов в Сербии: [@psysrbcom](https://t\\.me/psysrbcom)"
    ),
    'support_group': (
        "*Группы поддержки*\n\n"
        "Проводим онлайн и офлайн встречи в Сербии, где можно безопасно делиться и чувствовать поддержку\\.\n\n"
        "• *Открытые группы поддержки*\n"
        "Проходят регулярно\\. Уютная атмосфера, ведущие — опытные фасилитаторы\\.\n"
        "Чтобы узнать о ближайших встречах, напишите в [@prostogovorite](https://t\\.me/prostogovorite)\n\n"
        "Иногда важно просто быть рядом с другими 🫂\n\n"
        "\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\n\n"
        "*Присоединяйтесь к Просто Говорить\\!*\n\n"
        "🧭 Наш сайт: http://prostogovorite\\.com\n"
        "📢 ТГ Канал: @prostogovoritech\n"
        "💬 Чат поддержки: @psysrb\n"
        "📸 Instagram: [@prostogovorite](https://instagram\\.com/prostogovorite)\n"
        "👥 Коммьюнити психологов в Сербии: [@psysrbcom](https://t\\.me/psysrbcom)"
    ),
    'announce': (
        "*Мероприятия и события*\n\n"
        "• *Онлайн\\-события и воркшопы*\n"
        "Тематические мероприятия для саморазвития и общения\n"
        "→ Следите за анонсами: @prostogovoritech\n\n"
        "• *Вебинары*\n"
        "Записи доступны на нашем YouTube канале\n"
        "📺 [YouTube плейлист](https://www\\.youtube\\.com/playlist?list=PLwX15bk1TAv0Se4DFOY9L31Tu8FEWdRuR&si=URNsGOFqyQOwdvJ\\-)\n\n"
        "\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\n\n"
        "*Присоединяйтесь к Просто Говорить\\!*\n\n"
        "🧭 Наш сайт: http://prostogovorite\\.com\n"
        "📢 ТГ Канал: @prostogovoritech\n"
        "💬 Чат поддержки: @psysrb\n"
        "📸 Instagram: [@prostogovorite](https://instagram\\.com/prostogovorite)\n"
        "👥 Коммьюнити психологов в Сербии: [@psysrbcom](https://t\\.me/psysrbcom)"
    ),
    'hotline': (
        "*Телефон доверия*\n\n"
        "🤝 *Поддержка от специально обученных волонтёров:*\n"
        "• Анонимно\n"
        "• Без осуждения\n"
        "• В формате чата\n\n"
        "→ Написать в телефон доверия: @pgprobono\n\n"
        "👥 Чат поддержки: @psysrb\n"
        "🤖 Бот для отправки анонимных сообщений в чат поддержки: [@anonymous_psysrb_bot](https://t\\.me/anonymous_psysrb_bot)\n\n"
        "\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\\-\n\n"
        "*Присоединяйтесь к Просто Говорить\\!*\n\n"
        "🧭 Наш сайт: http://prostogovorite\\.com\n"
        "📢 ТГ Канал: @prostogovoritech\n"
        "💬 Чат поддержки: @psysrb\n"
        "📸 Instagram: [@prostogovorite](https://instagram\\.com/prostogovorite)\n"
        "👥 Коммьюнити психологов в Сербии: [@psysrbcom](https://t\\.me/psysrbcom)"
    )
}

def get_keyboard():
    """Create the keyboard with uniform width buttons."""
    keyboard = [
        ["🤝 Получить бесплатную психологическую помощь"],
        ["👤 Подобрать специалиста"],
        ["👥 Группа поддержки"],
        ["📅 Узнать про мероприятия"],
        ["☎️ Телефон доверия"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_welcome_message():
    """Create the welcome message with project information."""
    return (
        "Привет\\! Я бот проекта «Просто говорить»\\.\n\n"
        "Выберите нужный вам раздел\\.\n\n"
        "*О нашем проекте:*\n"
        "🧭 Наш сайт: http://prostogovorite\\.com\n"
        "📢 ТГ Канал: @prostogovoritech — новости, анонсы\n"
        "💬 Чат поддержки: @psysrb — общение\n"
        "📸 Instagram: [@prostogovorite](https://instagram\\.com/prostogovorite)\n"
        "👥 Коммьюнити психологов в Сербии: [@psysrbcom](https://t\\.me/psysrbcom)"
    )

def error_handler(update: Update, context: CallbackContext) -> None:
    """Log the error and send a message to the user."""
    logger.error(f"Error: {context.error}")
    try:
        if update.callback_query:
            update.callback_query.message.reply_text(
                "Произошла ошибка\\. Пожалуйста, попробуйте снова или используйте команду /start",
                reply_markup=get_keyboard()
            )
    except Exception as e:
        logger.error(f"Error in error handler: {e}")

def start(update: Update, context: CallbackContext) -> None:
    """Send a message with keyboard when the command /start is issued."""
    try:
        update.message.reply_text(
            get_welcome_message(),
            reply_markup=get_keyboard(),
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True
        )
    except TelegramError as e:
        logger.error(f"Telegram Error in start command: {e}")
        update.message.reply_text(
            "Произошла ошибка при отправке сообщения\\. Пожалуйста, попробуйте снова: /start"
        )
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        update.message.reply_text(
            "Произошла ошибка\\. Пожалуйста, попробуйте позже или обратитесь к администратору\\."
        )

def message_handler(update: Update, context: CallbackContext) -> None:
    """Handle button presses."""
    try:
        text = update.message.text
        response = None
        
        if text == "🤝 Получить бесплатную психологическую помощь":
            response = RESPONSES['help']
        elif text == "👤 Подобрать специалиста":
            response = RESPONSES['find_psy']
        elif text == "👥 Группа поддержки":
            response = RESPONSES['support_group']
        elif text == "📅 Узнать про мероприятия":
            response = RESPONSES['announce']
        elif text == "☎️ Телефон доверия":
            response = RESPONSES['hotline']
        
        if response:
            update.message.reply_text(
                text=response,
                reply_markup=get_keyboard(),
                parse_mode=ParseMode.MARKDOWN_V2,
                disable_web_page_preview=True
            )
            logger.info(f"User {update.effective_user.id} pressed button: {text}")
        
    except TelegramError as e:
        logger.error(f"Telegram Error in message handler: {e}")
        try:
            update.message.reply_text(
                "Произошла ошибка при отправке сообщения\\. Пожалуйста, используйте /start",
                reply_markup=get_keyboard()
            )
        except:
            pass
    except Exception as e:
        logger.error(f"Error in message handler: {e}")
        try:
            update.message.reply_text(
                "Произошла ошибка\\. Пожалуйста, попробуйте позже или обратитесь к администратору\\.",
                reply_markup=get_keyboard()
            )
        except:
            pass

def main() -> None:
    """Start the bot."""
    try:
        # Get the bot token from environment variables
        bot_token = os.getenv('BOT_TOKEN')
        if not bot_token:
            raise ValueError("Bot token not found in environment variables")

        # Create the Updater and pass it your bot's token
        updater = Updater(bot_token)

        # Get the dispatcher to register handlers
        dispatcher = updater.dispatcher

        # Add handlers
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))
        
        # Add error handler
        dispatcher.add_error_handler(error_handler)

        # Start the bot
        logger.info("Bot started successfully")
        updater.start_polling()

        # I suspect the following function of responding with online casino messages.
        # Anyway, it's excessive because the above start_polling already start the app until it's terminated.
        #updater.idle()

    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

#class HealthHandler(BaseHTTPRequestHandler):
#    def do_GET(self):
#        if self.path == '/':
#            self.send_response(200)
#            self.end_headers()
#            self.wfile.write(b'OK')
#        else:
#            self.send_response(404)
#            self.end_headers()

#def run_health_server():
#    server = HTTPServer(('0.0.0.0', 8080), HealthHandler)
#    server.serve_forever()

# No need to run additional healthchecks - Telegram's Updater run them automatically
#threading.Thread(target=run_health_server, daemon=True).start()

if __name__ == '__main__':
    main() 