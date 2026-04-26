import asyncio
import importlib

from aiohttp import web
from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from BrandrdXMusic import LOGGER, app, userbot
from BrandrdXMusic.core.call import Hotty
from BrandrdXMusic.misc import sudo
from BrandrdXMusic.plugins import ALL_MODULES
from BrandrdXMusic.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS


# ── Health server — Render ke liye port 8080 open karta hai ──────────────────
async def health(request):
    return web.Response(text="Bot is running!")


async def start_web():
    web_app = web.Application()
    web_app.router.add_get("/", health)
    web_app.router.add_get("/health", health)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    LOGGER("BrandrdXMusic").info("Health server started on port 8080")
# ─────────────────────────────────────────────────────────────────────────────


async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error(
            "No assistant STRING session defined! Please set at least one STRING variable."
        )
        exit()

    # Sabse pehle web server start karo — Render port scan karta hai
    await start_web()

    await sudo()

    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except Exception:
        pass

    await app.start()

    for all_module in ALL_MODULES:
        importlib.import_module("BrandrdXMusic.plugins" + all_module)
    LOGGER("BrandrdXMusic.plugins").info("Successfully Imported Modules...")

    await userbot.start()
    await Hotty.start()

    try:
        await Hotty.stream_call("https://graph.org/file/e999c40cb700e7c684b75.mp4")
    except NoActiveGroupCall:
        LOGGER("BrandrdXMusic").error(
            "Please turn on the videochat of your log group/channel.\n\nStopping Bot..."
        )
        exit()
    except Exception:
        pass

    await Hotty.decorators()

    LOGGER("BrandrdXMusic").info("Music Bot Started Successfully!")

    await idle()

    await app.stop()
    await userbot.stop()
    LOGGER("BrandrdXMusic").info("Bot stopped.")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
    
