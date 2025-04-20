import logging

from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.base import JobLookupError
from telegram import ReplyKeyboardMarkup

from const import REGULAR_CHECKIN_BUTTONS
from db.access import get_all_active_users

logger = logging.getLogger(__name__)


async def add_checkin_job(bot, scheduler, user_id: int, time_str: str) -> None:
    hour, minute = map(int, time_str.split(":"))

    job_id = f"checkin_{user_id}"
    try:
        scheduler.remove_job(job_id=job_id, jobstore=None)
    except JobLookupError:
        logger.warning(f"[SCHEDULER] no job found with job_id={job_id}")

    scheduler.add_job(
        send_checkin_message,
        trigger=CronTrigger(hour=hour, minute=minute),
        args=[bot, user_id],
        id=job_id,
        replace_existing=True,
    )

async def send_checkin_message(bot, user_id: int) -> None:
    try:
        await bot.send_message(
            chat_id=user_id,
            text="Готовий до чек-іну?",
            reply_markup=ReplyKeyboardMarkup(
                REGULAR_CHECKIN_BUTTONS,
                one_time_keyboard=True,
            ),
        )
    except Exception as e:
        logger.error(f"[SCHEDULER] ⚠️ Failed to send message {user_id}: {e}")

async def reschedule_job_after_restart(pool, bot, scheduler) -> None:
    users = await get_all_active_users()
    for user in users:
        await add_checkin_job(bot, scheduler, user_id=user.telegram_id, time_str=user.checkin_time)
    logging.info("[SCHEDULER] Rescheduling existing jobs complete.")
