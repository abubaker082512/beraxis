import asyncio
import os
import sys

# Add current dir to path
sys.path.append(os.getcwd())

from app.database import engine, Base
# Import all models so they are registered with Base.metadata
from app.models import user, campaign, call, agent, billing  # Use exact names found in list_dir

async def init_db():
    print("Creating tables...")
    try:
        async with engine.begin() as conn:
            # Optionally drop all if you want a clean start, 
            # but usually create_all is enough for new setups
            await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully!")
    except Exception as e:
        print(f"Error creating tables: {e}")

if __name__ == "__main__":
    asyncio.run(init_db())
