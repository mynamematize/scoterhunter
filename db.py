import aiosqlite
from datetime import datetime, timezone

DB_PATH = "scooters.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS listings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                buy_price REAL NOT NULL,
                repair_cost REAL NOT NULL DEFAULT 0,
                delivery_cost REAL NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)
        await db.commit()

async def add_listing(url: str, buy_price: float, repair_cost: float, delivery_cost: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO listings (url, buy_price, repair_cost, delivery_cost, created_at) VALUES (?, ?, ?, ?, ?)",
            (url, buy_price, repair_cost, delivery_cost, datetime.now(timezone.utc).isoformat())
        )
        await db.commit()

async def get_recent_listings(limit: int = 10):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT url, buy_price, repair_cost, delivery_cost, created_at FROM listings ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
