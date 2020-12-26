import asyncio

from pyrogram import Client
from configparser import ConfigParser, NoSectionError
from nana import app_version

config = ConfigParser()
config.read("config.ini")

try:
    APP_ID = int(config.get("nana", "api_id"))
    API_HASH = config.get("nana", "api_hash")
except NoSectionError:
    APP_ID = int(input("enter Telegram APP ID: "))
    API_HASH = input("enter Telegram API HASH: ")


async def main(api_id: int, api_hash: str, APP_VERSION: str):
    """generate StringSession for the current MemorySession"""
    async with Client(
        ":memory:", api_id=api_id, api_hash=api_hash, app_version=APP_VERSION
    ) as app:
        print((await app.export_session_string()))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(APP_ID, API_HASH, app_version))
