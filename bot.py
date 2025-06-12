import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext
)
from telegram.error import TelegramError

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Constants
RESPONSES = {
    'help': (
        "🤝 *Бесплатная психологическая помощь*\n\n"
        "До 10 сессий с проверенным специалистом. Подходит тем, кто испытывает финансовые трудности.\n\n"
        "→ Напишите координатору: @kondrashkin\\_pro\n\n"
        "Также доступна поддержка от специально обученных волонтёров:\n"
        "→ Позвонить или написать: @pgprobono\n\n"
        "Помощь оказывается конфиденциально 🫂"
    ),
    'find_psy': (
        "👤 *Подбор психолога*\n\n"
        "Ищете специалиста, который подойдёт именно вам? "
        "Наш бот поможет подобрать психолога, учитывая ваш запрос, язык общения и другие важные параметры. "
        "Это конфиденциально.\n\n"
        "→ Начать подбор через специализированного бота: @PsyGovoritBOT\n\n"
        "Также вы можете посмотреть каталог специалистов на нашем сайте:\n"
        "→ http://prostogovorite.com"
    ),
    'support_group': (
        "👥 *Группы поддержки*\n\n"
        "Проводим онлайн и офлайн встречи в Сербии, где можно безопасно делиться и чувствовать поддержку.\n\n"
        "• *Открытые группы поддержки*\n"
        "Проходят регулярно. Уютная атмосфера, ведущие — опытные фасилитаторы.\n"
        "→ Узнать о ближайших встречах: @prostogovoritech\n\n"
        "Иногда важно просто быть рядом с другими 🤗"
    ),
    'announce': (
        "📅 *Мероприятия и события*\n\n"
        "• *Онлайн\\-события и воркшопы*\n"
        "Тематические мероприятия для саморазвития и общения\n"
        "→ Следите за анонсами: @prostogovoritech\n\n"
        "• *Вебинары*\n"
        "Записи доступны на нашем YouTube канале\n"
        "→ [Смотреть записи](https://www\\.youtube\\.com/playlist?list=PLwX15bk1TAv0Se4DFOY9L31Tu8FEWdRuR)\n\n"
        "📢 Подписывайтесь на наши ресурсы:\n"
        "• [Канал «Просто говорить»](https://t\\.me/prostogovoritech)\n"
        "• [Instagram](https://www\\.instagram\\.com/prostogovorite)"
    ),
    'hotline': (
        "☎️ *Телефон доверия*\n\n"
        "Поддержка от специально обученных волонтёров:\n"
        "• Анонимно\n"
        "• Без осуждения\n"
        "• В формате чата\n\n"
        "→ Написать в телефон доверия: @pgprobono\n\n"
        "🤫 Также доступен бот для анонимных сообщений:\n"
        "→ @anonymous\\_psysrb\\_bot\n"
        "• Поделиться историей\n"
        "• Задать вопрос\n"
        "• Получить поддержку"
    ),
    'about': (
        "ℹ️ *О проекте «Просто говорить»*\n\n"
        "🧭 Наш сайт → http://prostogovorite.com\n\n"
        "📡 Наши ресурсы:\n"
        "• [Канал](https://t.me/prostogovoritech) — новости, статьи, анонсы\n"
        "• [Чат поддержки](https://t.me/psysrb) — общение, поддержка\n"
        "• [Чат для психологов](https://t.me/psysrbcom) — профессиональное сообщество\n"
        "• [Instagram](https://www.instagram.com/prostogovorite) — посты о психологии и жизни в Сербии"
    )
}

def get_keyboard():
    """Create the keyboard with uniform width buttons."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🤝 Получить бесплатную психологическую помощь", callback_data='help')],
        [InlineKeyboardButton("👤 Подобрать специалиста", callback_data='find_psy')],
        [InlineKeyboardButton("👥 Группа поддержки", callback_data='support_group')],
        [InlineKeyboardButton("📅 Узнать про мероприятия", callback_data='announce')],
        [InlineKeyboardButton("☎️ Телефон доверия", callback_data='hotline')],
    ])

def get_welcome_message():
    """Create the welcome message with project information."""
    return (
        "Привет! Я бот проекта «Просто говорить»\\.\n\n"
        "Выберите нужный вам раздел:\n\n"
        "📡 *О нашем проекте:*\n"
        "• [Сайт](http://prostogovorite\\.com) — каталог специалистов и информация о проекте\n"
        "• [Канал](https://t\\.me/prostogovoritech) — новости, статьи, анонсы\n"
        "• [Чат поддержки](https://t\\.me/psysrb) — общение, поддержка\n"
        "• [Instagram](https://www\\.instagram\\.com/prostogovorite) — посты о психологии и жизни в Сербии"
    )

def error_handler(update: Update, context: CallbackContext) -> None:
    """Log the error and send a message to the user."""
    logger.error(f"Error: {context.error}")
    try:
        if update.callback_query:
            update.callback_query.message.reply_text(
                "Произошла ошибка. Пожалуйста, попробуйте снова или используйте команду /start",
                reply_markup=get_keyboard()
            )
    except Exception as e:
        logger.error(f"Error in error handler: {e}")

def start(update: Update, context: CallbackContext) -> None:
    """Send a message with inline buttons when the command /start is issued."""
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
            "Произошла ошибка при отправке сообщения. Пожалуйста, попробуйте снова: /start"
        )
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        update.message.reply_text(
            "Произошла ошибка. Пожалуйста, попробуйте позже или обратитесь к администратору."
        )

def button_handler(update: Update, context: CallbackContext) -> None:
    """Handle button presses."""
    try:
        query = update.callback_query
        query.answer()

        # Get response for the button pressed
        response = RESPONSES.get(query.data, "Неизвестная команда.")
        
        # Edit the message with the response and keep the keyboard
        query.edit_message_text(
            text=response,
            reply_markup=get_keyboard(),
            parse_mode=ParseMode.MARKDOWN_V2,
            disable_web_page_preview=True
        )
        
        # Log the interaction
        logger.info(f"User {update.effective_user.id} pressed button: {query.data}")
        
    except TelegramError as e:
        logger.error(f"Telegram Error in button handler: {e}")
        try:
            query.edit_message_text(
                "Произошла ошибка при отправке сообщения. Пожалуйста, используйте /start",
                reply_markup=get_keyboard()
            )
        except:
            pass
    except Exception as e:
        logger.error(f"Error in button handler: {e}")
        try:
            query.edit_message_text(
                "Произошла ошибка. Пожалуйста, попробуйте позже или обратитесь к администратору.",
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
        dispatcher.add_handler(CallbackQueryHandler(button_handler))
        
        # Add error handler
        dispatcher.add_error_handler(error_handler)

        # Start the bot
        logger.info("Bot started successfully")
        updater.start_polling()

        # Run the bot until you press Ctrl-C
        updater.idle()

    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    main() 