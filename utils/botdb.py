import os

import asyncpg
import motor.motor_asyncio
from colorama import Fore
from dotenv import load_dotenv

from ext import consts

load_dotenv()


async def mongo_connection():
    cluster: motor.motor_asyncio.AsyncIOMotorClient = (
        motor.motor_asyncio.AsyncIOMotorClient(os.getenv("mongo_uri"))
    )
    return cluster["webdb"]


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

    dsn = os.getenv("postgres")
    return await asyncpg.create_pool(dsn=dsn)


async def create_table(conn: asyncpg.Connection):
    await conn.execute(consts.AFK_CONFIG_SCHEMA)
    print(Fore.CYAN + "setup: afk")
    await conn.execute(consts.GIVEAWAY_CONFIG_SCHEMA)
    print(Fore.CYAN + "setup: gaway")
    await conn.execute(consts.LEVELLING_CONFIG_SCHEMA)
    print(Fore.CYAN + "setup: level")
    await conn.execute(consts.WARNING_CONFIG_SCHEMA)
    print(Fore.CYAN + "setup: warns")
    await conn.execute(consts.TODO_CONFIG_SCHEMA)
    print(Fore.CYAN + "setup: todo")
    await conn.execute(consts.REMINDER_CONFIG_SCHEMA)
    print(Fore.CYAN + "setup: reminder")


async def delete_table(conn: asyncpg.Connection, table: str = None):
    if table is None:
        return print(Fore.RED + "no table specified")
    await conn.execute(f"DROP TABLE IF EXISTS {table}")
    print(Fore.RED + "deleted: " + table)
