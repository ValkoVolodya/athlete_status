import os
import asyncpg
import logging

from telegram.ext import Application


async def on_startup(app: Application) -> None:
    logging.info("Connecting to the DB...")
    app.bot_data["db"] = await asyncpg.connect(f'postgresql://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@db/{os.getenv("POSTGRES_DB")}')
    logging.info("Connected to DB ✅")

async def on_shutdown(app: Application) -> None:
    db = app.bot_data.get("db")
    if db:
        await db.close()
        logging.warning("DB connection closed ❌")
