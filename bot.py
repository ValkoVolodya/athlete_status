from datetime import datetime
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

from const import (
    ANSWER_BUTTONS,
    CHECKIN_TIMES,
    DEFAULT_REPLY_BUTTONS,
    SKIP_CHECKIN_TEXT,
    START_CHECKIN_TEXT,
    YES_REPLY,
)
from db.access import (
    create_checkin,
    get_checkins,
    get_or_create_user,
)
from bot_setup import on_shutdown, on_startup
from scheduler import add_checkin_job


QUESTIONS_LIST = [
    "✅ Чи добре я відновився після попереднього тренування?",
    "✅ Чи мій ранковий пульс у нормі (±5 уд/хв від звичного)?",
    "✅ Чи я виспався (7–8 годин сну, без нічних пробуджень)?",
    "✅ Чи маю мотивацію тренуватись або хоча б настрій “норм”?",
    "✅ Чи мій апетит нормальний (не надто слабкий і не занадто дикий)?",
    "✅ Чи почуваюся спокійним, без роздратованості?",
    "✅ Чи ноги відчуваються “живими” після короткої розминки?",
]


def get_recomendation_text_by_score(score: int) -> str:
    if score <= 3:
        return "Краще зроби день відпочинку або легке катання в Z1-Z2 🧘"
    if score <= 5:
        return "Поміркуй над легшим тренуванням або коротким Sweet Spot"
    if score <= 7:
        return "Все ок! Тренуйся на максимум 🚴‍♂️"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await get_or_create_user(context.bot_data['pool'], telegram_id=user.id)
    await update.message.reply_html(
        rf"Привіт, {user.mention_html()}! "
        rf"Я створений для зручної щоденної перевірки "
        rf"твого стану готовності до тренування. "
        rf"О котрій годині тобі зручно отримувати щоденний чек-ін?",
        reply_markup=ReplyKeyboardMarkup(CHECKIN_TIMES, one_time_keyboard=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Help!")


async def choose_checkin_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    time_str = update.message.text.strip()

    try:
        async with context.application.bot_data["pool"].acquire() as conn:
            await conn.execute(
                "UPDATE users SET checkin_time = $1 WHERE telegram_id = $2",
                datetime.strptime(time_str, "%H:%M"),
                update.effective_user.id,
            )
        await add_checkin_job(
            context.bot,
            context.application.bot_data['scheduler'],
            update.effective_user.id,
            time_str,
        )
        await update.message.reply_text(rf"Чек-ін буде надсилатись щодня о {time_str} 🕒")
    except ValueError:
        await update.message.reply_text(
            "Неправильний формат часу. Будь ласка, обери зі списку",
            reply_markup=ReplyKeyboardMarkup(CHECKIN_TIMES, one_time_keyboard=True),
        )


async def checkin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['result'] = 0
    context.user_data['question_id'] = 0
    await update.message.reply_html(
        rf"Починаємо опитування: "
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
        await create_checkin(
            context.bot_data['pool'],
            telegram_id=update.effective_user.id,
            total_score=context.user_data["result"],
            recommendation=get_recomendation_text_by_score(context.user_data['result']),
        )
        await update.message.reply_html(
            rf"Твій результат: "
            rf"{context.user_data['result']} балів "
            rf"{get_recomendation_text_by_score(context.user_data['result'])}"
        )
        context.user_data.clear()
    else:
        await update.message.reply_html(
            rf"{QUESTIONS_LIST[context.user_data['question_id']]}"
        )

async def results_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    checkins = await get_checkins(context.bot_data['pool'], update.effective_user.id)
    print(checkins)
    res_text = ""
    for check in checkins:
        print(check)
        res_text += str(check.get('total_score')) + " | "
        res_text += check.get('recommendation') + " | "
        res_text += str(check.get('created_at').date()) + " | "
    await update.message.reply_html(
        rf"{res_text}"
    )


def main() -> None:
    logging.info("App started")
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("checkin", checkin_command))
    application.add_handler(CommandHandler("results", results_command))

    application.add_handler(
        MessageHandler(filters.Text(ANSWER_BUTTONS), choose_action_from_button)
    )
    application.add_handler(
        MessageHandler(filters.Regex(r"^\d{1,2}:\d{2}$"), choose_checkin_time)
    )
    application.add_handler(
        MessageHandler(filters.Text(START_CHECKIN_TEXT), checkin_command)
    )
    # application.add_handler(
    #     MessageHandler(filters.Text(SKIP_CHECKIN_TEXT), lambda())
    # )

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
