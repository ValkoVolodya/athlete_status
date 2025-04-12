import os
import logging

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from db import on_shutdown, on_startup


YES_REPLY = "Так"
NO_REPLY = "Ні"
DONT_KNOW_REPLY = "Не знаю"

DEFAULT_REPLY_BUTTONS = [
    [YES_REPLY],
    [NO_REPLY],
    [DONT_KNOW_REPLY],
]

QUESTIONS_LIST = [
    "✅ Чи добре я відновився після попереднього тренування?",
    "✅ Чи мій ранковий пульс у нормі (±5 уд/хв від звичного)?",
    "✅ Чи я виспався (7–8 годин сну, без нічних пробуджень)?",
    "✅ Чи маю мотивацію тренуватись або хоча б настрій “норм”?",
    "✅ Чи мій апетит нормальний (не надто слабкий і не занадто дикий)?",
    "✅ Чи почуваюся спокійним, без роздратованості?",
    "✅ Чи ноги відчуваються “живими” після короткої розминки?",
]


def get_reccomendation_text_by_score(score: int) -> str:
    if score <= 3:
        return "Краще зроби день відпочинку або легке катання в Z1-Z2 🧘"
    if score <= 5:
        return "Поміркуй над легшим тренуванням або коротким Sweet Spot"
    if score <= 7:
        return "Все ок! Тренуйся на максимум 🚴‍♂️"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Привіт, {user.mention_html()}! "
        rf"Я створений для зручної щоденної перевірки "
        "твого стану готовності до тренування.",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Help!")


async def checkin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['result'] = 0
    context.user_data['question_id'] = 0
    await update.message.reply_html(
        rf"Починаємо опитування:\n"
        rf"{QUESTIONS_LIST[0]}",
        reply_markup=ReplyKeyboardMarkup(DEFAULT_REPLY_BUTTONS),
    )

async def choose_action_from_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    question_id = context.user_data.get('question_id', 0)
    context.user_data['question_id'] = question_id + 1
    result = context.user_data.get('result', 0)
    if update.message.text == YES_REPLY:
        context.user_data['result'] = result + 1
    if context.user_data['question_id'] >= len(QUESTIONS_LIST):
        await update.message.reply_html(
            rf"Твій результат: "
            rf"{context.user_data['result']} балів "
            rf"{get_reccomendation_text_by_score(context.user_data['result'])}"
        )
        context.user_data['question_id'] = 0
        context.user_data['result'] = 0
    else:
        await update.message.reply_html(
            rf"{QUESTIONS_LIST[context.user_data['question_id']]}"
        )



def main() -> None:
    logging.info("App started")
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("checkin", checkin_command))

    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, choose_action_from_button)
    )

    application.post_init = on_startup
    application.post_shutdown = on_shutdown

    if os.getenv("DEPLOY"):
        application.run_webhook(
            listen='0.0.0.0',
            port=os.getenv("PORT"),
            webhook_url=os.getenv("WEBHOOK_URL"),
        )
    else:
        print("Run polling locally")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
