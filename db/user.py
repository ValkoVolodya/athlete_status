from asyncpg import Record


async def get_user_conn(conn, telegram_id: int) -> Record:
    return await conn.fetchrow(
        "SELECT * FROM users WHERE telegram_id = $1", telegram_id
    )

async def get_or_create_user_conn(conn, telegram_id: int) -> Record:
    if user := await get_user_conn(conn, telegram_id):
        return user

    await conn.execute(
        "INSERT INTO users (telegram_id) VALUES ($1)",
        telegram_id
    )
    return await get_user_conn(conn, telegram_id)