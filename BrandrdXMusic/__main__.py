import asyncio
import importlib
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from BrandrdXMusic import LOGGER, app, userbot
from BrandrdXMusic.core.call import Hotty
from BrandrdXMusic.misc import sudo
from BrandrdXMusic.plugins import ALL_MODULES
from BrandrdXMusic.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# KEEP ALIVE (RENDER FIX — INSTANT PORT)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

    def log_message(self, *args):
        pass


def run_server():
    port = int(os.environ.get("PORT", 8080))
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()


# Start immediately (CRITICAL)
threading.Thread(target=run_server, daemon=True).start()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN BOT LOGIC
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("Assistant client variables not defined, exiting...")
        exit()

    await sudo()

    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)

        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass

    await app.start()

    for module in ALL_MODULES:
        importlib.import_module("BrandrdXMusic.plugins." + module)

    LOGGER("BrandrdXMusic.plugins").info("Modules Imported")

    await userbot.start()
    await Hotty.start()

    try:
        await Hotty.stream_call(
            "https://graph.org/file/e999c40cb700e7c684b75.mp4"
        )
    except NoActiveGroupCall:
        LOGGER("BrandrdXMusic").error(
            "Turn on video chat in your log group/channel.\nStopping bot..."
        )
        exit()
    except:
        pass

    await Hotty.decorators()

    LOGGER("BrandrdXMusic").info("Bot Started Successfully")

    await idle()

    await app.stop()
    await userbot.stop()

    LOGGER("BrandrdXMusic").info("Stopping Bot...")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENTRY POINT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
