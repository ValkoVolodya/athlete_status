import os
import asyncpg
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram.ext import Application

scheduler = AsyncIOScheduler()


async def on_startup(app: Application) -> None:
    logging.info("Connecting to the DB...")
    app.bot_data["pool"] = await asyncpg.create_pool(os.getenv('POSTGRES_URI'))
    logging.info("Connected to DB ✅")
    logging.info("Starting scheduler...")
    app.bot_data["scheduler"] = scheduler
    logging.info("Scheduler started ✅")

async def on_shutdown(app: Application) -> None:
    pool = app.bot_data.get("pool")
    if pool:
        await pool.close()
        logging.warning("DB pool closed ❌")

