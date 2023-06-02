from dotenv import load_dotenv
import os

import asyncpg

from ext import consts
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
    await conn.execute(consts.AFK_CONFIG_SCHEMA)
    print('setup: afk')

async def delete_table(conn: asyncpg.Connection, table: str = None):
    if table is None:
        return print('no table specified')
    await conn.execute('DROP TABLE ?',(table))
    print('deleted: ' + table)