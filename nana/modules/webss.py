import os
from pyrogram import filters

from nana import (
    app,
    COMMAND_PREFIXES,
    THUMBNAIL_API,
    SCREENSHOTLAYER_API,
    AdminSettings,
    edit_or_reply,
)

__MODULE__ = "SS Website"
__HELP__ = """
Take a picture of website. You can select one for use this.

──「 **Take ss website** 」──
-> `print (url)`
Send web screenshot, not full webpage. Send as picture

──「 **Take ss website (more)** 」──
-> `ss (url) (*full)`
Take screenshot of that website, if `full` args given, take full of website and send image as document

* = optional
"""


@app.on_message(
    filters.user(AdminSettings) & filters.command("print", COMMAND_PREFIXES)
)
async def print_web(client, message):
    if len(message.text.split()) == 1:
        await edit_or_reply(message, text="Usage: `print web.url`")
        return
    if not THUMBNAIL_API:
        await edit_or_reply(message, text="You need to fill thumbnail_API to use this!")
        return
    args = message.text.split(None, 1)
    teks = args[1]
    teks = teks if "http://" in teks or "https://" in teks else "http://" + teks
    capt = f"Website: `{teks}`"
    await client.send_chat_action(message.chat.id, action="upload_photo")
    web_photo = f"https://api.thumbnail.ws/api/{THUMBNAIL_API}/thumbnail/get?url={teks}&width=1280"
    await message.delete()
    await client.send_photo(message.chat.id, photo=web_photo, caption=capt)


@app.on_message(filters.user(AdminSettings) & filters.command("ss", COMMAND_PREFIXES))
async def ss_web(client, message):
    if len(message.text.split()) == 1:
        await edit_or_reply(message, text="Usage: `print web.url`")
        return
    if not SCREENSHOTLAYER_API:
        await edit_or_reply(
            message, text="You need to fill screenshotlayer_API to use this!"
        )
        return
    args = message.text.split(None, 1)
    teks = args[1]
    full = False
    if len(message.text.split()) >= 3 and message.text.split(None, 2)[2] == "full":
        full = True

    teks = teks if "http://" in teks or "https://" in teks else "http://" + teks
    capt = f"Website: `{teks}`"

    await client.send_chat_action(message.chat.id, action="upload_photo")
    if full:
        r = f"http://api.screenshotlayer.com/api/capture?access_key={SCREENSHOTLAYER_API}&url={teks}&fullpage=1"
    else:
        r = f"http://api.screenshotlayer.com/api/capture?access_key={SCREENSHOTLAYER_API}&url={teks}&fullpage=0"
    await message.delete()
    await client.send_photo(message.chat.id, photo=r, caption=capt)
    os.remove("nana/cache/web.png")
    await client.send_chat_action(message.chat.id, action="cancel")
