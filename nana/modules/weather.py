import asyncio
import aiohttp
from html import escape

from pyrogram import filters

from nana import app, COMMAND_PREFIXES, AdminSettings, edit_or_reply, Owner
from nana.modules.database.lang_db import prev_locale


__MODULE__ = "Weather"
__HELP__ = """
Get current weather in your location

──「 **Weather** 」──
-> `wttr (location)`
Get current weather in your location.
Powered by `wttr.in`
"""


@app.on_message(
    filters.user(AdminSettings) & filters.command("wttr", prefixes=COMMAND_PREFIXES)
)
async def weather(_, message):
    if len(message.command) == 1:
        await edit_or_reply(message, text="Usage: `wttr Maldives`")
        await asyncio.sleep(3)
        await message.delete()

    if len(message.command) > 1:
        location = message.command[1]
        headers = {"user-agent": "httpie"}
        url = f"https://wttr.in/{location}?mnTC0&lang={prev_locale(Owner).locale_name}"
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as resp:
                data = await resp.text()
        if "we processed more than 1M requests today" in data:
            await edit_or_reply(
                message, text="`Sorry, we cannot process this request today!`"
            )
        else:
            weather_data = f"<code>{escape(data.replace('report', 'Report'))}</code>"
            await edit_or_reply(message, text=weather_data, parse_mode="html")
