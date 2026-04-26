import asyncio
import os
import re
import json
import glob
import random
from typing import Union

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch

from BrandrdXMusic.utils.formatters import time_to_seconds
from BrandrdXMusic import LOGGER


# ── Cookie file selector ──────────────────────────────────────────────────────
def cookie_txt_file():
    folder_path = f"{os.getcwd()}/cookies"
    filename = f"{os.getcwd()}/cookies/logs.csv"
    os.makedirs(folder_path, exist_ok=True)
    txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
    if not txt_files:
        return None  # cookies nahi hain toh None return karo, crash mat karo
    cookie_txt = random.choice(txt_files)
    try:
        with open(filename, "a") as file:
            file.write(f"Chosen File: {cookie_txt}\n")
    except:
        pass
    return f"cookies/{str(cookie_txt).split('/')[-1]}"
# ─────────────────────────────────────────────────────────────────────────────


def get_ydl_opts(extra: dict = {}) -> dict:
    """Base yt-dlp options — cookie optional"""
    opts = {
        "geo_bypass": True,
        "nocheckcertificate": True,
        "quiet": True,
        "no_warnings": True,
        **extra,
    }
    cookie = cookie_txt_file()
    if cookie:
        opts["cookiefile"] = cookie
    return opts


async def clean_old_downloads():
    """Purani files delete karo — disk free rakho"""
    try:
        folder = "downloads"
        if not os.path.exists(folder):
            return
        files = sorted(
            [os.path.join(folder, f) for f in os.listdir(folder)],
            key=os.path.getmtime,
        )
        if len(files) > 10:
            for f in files[:-10]:
                try:
                    os.remove(f)
                except:
                    pass
    except:
        pass


async def check_file_size(link):
    cookie = cookie_txt_file()
    cmd = ["yt-dlp", "-J", link]
    if cookie:
        cmd = ["yt-dlp", "--cookies", cookie, "-J", link]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        return None
    try:
        info = json.loads(stdout.decode())
        total = sum(f.get("filesize", 0) or 0 for f in info.get("formats", []))
        return total
    except:
        return None


async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in errorz.decode("utf-8").lower():
            return out.decode("utf-8")
        return errorz.decode("utf-8")
    return out.decode("utf-8")


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset is None:
            return None
        return text[offset: offset + length]

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            duration_sec = 0 if str(duration_min) == "None" else int(time_to_seconds(duration_min))
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["title"]

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["duration"]

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["thumbnails"][0]["url"].split("?")[0]

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        cookie = cookie_txt_file()
        cmd = ["yt-dlp", "-g", "-f", "best[height<=?480][width<=?854]", link]
        if cookie:
            cmd = ["yt-dlp", "--cookies", cookie, "-g", "-f", "best[height<=?480][width<=?854]", link]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if stdout:
            return 1, stdout.decode().split("\n")[0]
        return 0, stderr.decode()

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        cookie = cookie_txt_file()
        cookie_part = f"--cookies {cookie}" if cookie else ""
        playlist = await shell_cmd(
            f"yt-dlp -i --get-id --flat-playlist {cookie_part} --playlist-end {limit} --skip-download {link}"
        )
        try:
            result = [key for key in playlist.split("\n") if key]
        except:
            result = []
        return result

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            vidid = result["id"]
            yturl = result["link"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        ytdl_opts = get_ydl_opts()
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for format in r["formats"]:
                try:
                    if "dash" not in str(format["format"]).lower():
                        formats_available.append({
                            "format": format["format"],
                            "filesize": format.get("filesize"),
                            "format_id": format["format_id"],
                            "ext": format["ext"],
                            "format_note": format["format_note"],
                            "yturl": link,
                        })
                except:
                    continue
        return formats_available, link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        if videoid:
            link = self.base + link

        await clean_old_downloads()
        loop = asyncio.get_running_loop()

        def audio_dl():
            opts = get_ydl_opts({
                "format": "bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
            })
            x = yt_dlp.YoutubeDL(opts)
            info = x.extract_info(link, False)
            xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            if os.path.exists(xyz):
                return xyz
            x.download([link])
            return xyz

        def video_dl():
            opts = get_ydl_opts({
                # 480p max — lag kam hoga Render pe
                "format": "(bestvideo[height<=?480][width<=?854][ext=mp4])+(bestaudio[ext=m4a])/best[height<=?480]/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "merge_output_format": "mp4",
            })
            x = yt_dlp.YoutubeDL(opts)
            info = x.extract_info(link, False)
            xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            if os.path.exists(xyz):
                return xyz
            x.download([link])
            return xyz

        def song_video_dl():
            opts = get_ydl_opts({
                "format": f"{format_id}+140",
                "outtmpl": f"downloads/{title}",
                "prefer_ffmpeg": True,
                "merge_output_format": "mp4",
            })
            yt_dlp.YoutubeDL(opts).download([link])

        def song_audio_dl():
            opts = get_ydl_opts({
                "format": format_id,
                "outtmpl": f"downloads/{title}.%(ext)s",
                "prefer_ffmpeg": True,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "128",
                }],
            })
            yt_dlp.YoutubeDL(opts).download([link])

        if songvideo:
            await loop.run_in_executor(None, song_video_dl)
            return f"downloads/{title}.mp4"

        elif songaudio:
            await loop.run_in_executor(None, song_audio_dl)
            return f"downloads/{title}.mp3"

        elif video:
            # Direct stream URL try karo pehle — no download, no lag
            cookie = cookie_txt_file()
            cmd = ["yt-dlp", "-g", "-f", "best[height<=?480][width<=?854]", link]
            if cookie:
                cmd = ["yt-dlp", "--cookies", cookie, "-g", "-f", "best[height<=?480][width<=?854]", link]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            if stdout:
                # Direct stream — sabse smooth, download nahi hoga
                return stdout.decode().split("\n")[0], False
            else:
                # Fallback: file download karo
                file_size = await check_file_size(link)
                if file_size:
                    total_mb = file_size / (1024 * 1024)
                    if total_mb > 250:
                        LOGGER("BrandrdXMusic.platforms.Youtube").error(
                            f"File too large: {total_mb:.2f} MB"
                        )
                        return None, False
                downloaded_file = await loop.run_in_executor(None, video_dl)
                return downloaded_file, True

        else:
            downloaded_file = await loop.run_in_executor(None, audio_dl)
            return downloaded_file, True
        
