import asyncio
import asyncpg

async def test_conn(user, password, db):
    try:
        url = f'postgresql://{user}:{password}@localhost:5432/{db}'
        print(f"Testing {url}...")
        conn = await asyncio.wait_for(asyncpg.connect(url), timeout=5)
        print(f"SUCCESS: {url}")
        await conn.close()
        return True
    except Exception as e:
        print(f"FAIL: {user}@{db}: {e}")
        return False

async def main():
    variations = [
        ('beraxis_user', 'beraxis_pass', 'beraxis_db'),
        ('beraxis', 'beraxis_pass', 'beraxis_db'),
        ('postgres', 'postgres', 'postgres'),
        ('postgres', '', 'postgres'),
    ]
    for u, p, d in variations:
        if await test_conn(u, p, d):
            print(f"FOUND_CREDENTIALS: {u}:{p}@{d}")
            # Try to check if beraxis_db exists if we used postgres user
            if u == 'postgres':
                 try:
                    conn = await asyncpg.connect(f'postgresql://{u}:{p}@localhost:5432/postgres')
                    exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = 'beraxis_db'")
                    print(f"beraxis_db exists: {exists == 1}")
                    await conn.close()
                 except: pass
            break

if __name__ == "__main__":
    asyncio.run(main())
