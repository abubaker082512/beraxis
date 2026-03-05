import asyncio
import asyncpg
import redis
import sys
import os

# Add parent dir to path to import app
sys.path.append(os.getcwd())
from app.config import settings

async def check_db():
    print(f"Checking DB: {settings.DATABASE_URL}...")
    try:
        conn = await asyncpg.connect(settings.DATABASE_URL)
        val = await conn.fetchval('SELECT 1')
        print(f"DB Ping: {val}")
        await conn.close()
        return True
    except Exception as e:
        print(f"DB Error: {e}")
        return False

def check_redis():
    print(f"Checking Redis: {settings.REDIS_URL}...")
    try:
        r = redis.from_url(settings.REDIS_URL)
        ping = r.ping()
        print(f"Redis Ping: {ping}")
        return True
    except Exception as e:
        print(f"Redis Error: {e}")
        return False

async def main():
    db_ok = await check_db()
    redis_ok = check_redis()
    if db_ok and redis_ok:
        print("INFRA_OK")
        sys.exit(0)
    else:
        print("INFRA_FAIL")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
