from asyncpg import Record

from db.checkins import create_checkin_conn, get_checkins_conn
from db.user import get_or_create_user_conn, get_user_conn, get_all_active_users_conn


async def get_user(pool, telegram_id: int) -> Record:
    async with pool.acquire() as conn:
        return await get_user_conn(conn, telegram_id)

async def get_or_create_user(pool, telegram_id: int) -> Record:
    async with pool.acquire() as conn:
        return await get_or_create_user_conn(conn, telegram_id)

async def create_checkin(pool, telegram_id: int, total_score: int, recommendation: str):
    async with pool.acquire() as conn:
        return await create_checkin_conn(conn, telegram_id, total_score, recommendation)

async def get_checkins(pool, telegram_id: int) -> list[Record]:
    async with pool.acquire() as conn:
        return await get_checkins_conn(conn, telegram_id=telegram_id)

async def get_all_active_users(pool) -> list[Record]:
    async with pool.acquire() as conn: 
        return await get_all_active_users_conn(conn)
