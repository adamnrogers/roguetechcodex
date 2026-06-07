import aiosqlite
import os

DB_PATH = os.environ.get("DB_PATH", "roguetech.db")


async def get_db():
    # immutable=1 bypasses WAL fcntl locking, which fails in aiosqlite's thread
    # pool on Docker Desktop Windows virtual filesystems.
    uri = f"file:{DB_PATH}?immutable=1"
    async with aiosqlite.connect(uri, uri=True) as db:
        db.row_factory = aiosqlite.Row
        yield db
