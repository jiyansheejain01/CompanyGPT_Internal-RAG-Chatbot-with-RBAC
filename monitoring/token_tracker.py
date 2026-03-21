from auth.models import engine
from sqlalchemy import text
from datetime import datetime


def log_token_usage(username: str, prompt_tokens: int, completion_tokens: int):
    total = prompt_tokens + completion_tokens
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO token_usage (username, prompt_tokens, completion_tokens, total_tokens, timestamp)
            VALUES (:username, :prompt, :completion, :total, :ts)
        """), {
            "username": username,
            "prompt": prompt_tokens,
            "completion": completion_tokens,
            "total": total,
            "ts": datetime.utcnow()
        })
        conn.commit()


def get_usage_summary() -> list[dict]:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT username,
                   COUNT(*) as total_queries,
                   SUM(total_tokens) as total_tokens,
                   SUM(prompt_tokens) as prompt_tokens,
                   SUM(completion_tokens) as completion_tokens
            FROM token_usage
            GROUP BY username
            ORDER BY total_tokens DESC
        """))
        return [dict(row._mapping) for row in result]


def get_daily_usage() -> list[dict]:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT DATE(timestamp) as date,
                   SUM(total_tokens) as total_tokens,
                   COUNT(*) as total_queries
            FROM token_usage
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
            LIMIT 30
        """))
        return [dict(row._mapping) for row in result]


def check_daily_alert(threshold: int = 100000) -> tuple[bool, int]:
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT COALESCE(SUM(total_tokens), 0) as today_tokens
            FROM token_usage
            WHERE DATE(timestamp) = DATE('now')
        """))
        today_tokens = result.fetchone()[0]
        return today_tokens > threshold, today_tokens
