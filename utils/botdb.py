from dotenv import load_dotenv
import os

import asyncpg

load_dotenv()

async def connection() -> asyncpg.Connection:
    
    """
    You can connect in both ways using dsn or user
    """
    
    # user = os.getenv('postgres_user')
    # password = os.getenv('postgres_pass')
    # db = os.getenv('postgres_db')
    # host = os.getenv('postgres_host')
    # port = os.getenv('postgres_port')
    # return await asyncpg.connect(host=host, port=port, user=user, password=password, database=db)


    dsn=os.getenv('postgres')
    return await asyncpg.connect(dsn=dsn)


async def create_table(conn: asyncpg.Connection):
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS afk (
            user_id BIGINT,
            afk_reason TEXT,
            time BIGINT
        )
    ''')
    print('setup: afk')

async def delete_table(conn: asyncpg.Connection):
    await conn.execute('DROP TABLE afk')
    print('deleted: afks')