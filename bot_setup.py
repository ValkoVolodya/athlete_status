import os
import asyncpg
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram.ext import Application

from scheduler import reschedule_job_after_restart

scheduler = AsyncIOScheduler()


async def on_startup(app: Application) -> None:
    logging.info("[BOT_SETUP] Connecting to the DB...")
    app.bot_data["pool"] = await asyncpg.create_pool(os.getenv('POSTGRES_URI'))
    logging.info("[BOT_SETUP] Connected to DB ✅")
    app.bot_data["scheduler"] = scheduler
    scheduler.start()
    logging.info("[BOT_SETUP] Scheduler started ✅")
    await reschedule_job_after_restart(app.bot_data["pool"], app.bot, scheduler)


async def on_shutdown(app: Application) -> None:
    pool = app.bot_data.get("pool")
    if pool:
        await pool.close()
        logging.warning("[BOT_SETUP] DB pool closed ❌")

