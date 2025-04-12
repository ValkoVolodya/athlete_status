

async def create_checkin_conn(conn, telegram_id: int, total_score: int, recomendation: str):
    return await conn.execute(
        "INSERT INTO checkins (telegram_id, total_score, recommendation) VALUES ($1, $2, $3)",
        telegram_id, total_score, recomendation,
    )
