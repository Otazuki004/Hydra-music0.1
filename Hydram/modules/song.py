from pyrogram import Client, filters
import asyncio
import os
from pytube import YouTube
from pyrogram.types import InlineKeyboardMarkup
from pyrogram.types import InlineKeyboardButton
from youtubesearchpython import VideosSearch
from Hydram.H import ignore_blacklisted_users, get_arg
from Hydram import app, LOGGER
from Hydram.sql.chat_sql import add_chat_to_db


def yt_search(song):
    videosSearch = VideosSearch(song, limit=1)
    result = videosSearch.result()
    if not result:
        return False
    else:
        video_id = result["result"][0]["id"]
        url = f"https://youtu.be/{video_id}"
        return url


@app.on_message(filters.create(ignore_blacklisted_users) & filters.command("song"))
async def song(client, message):
    chat_id = message.chat.id
    user_id = message.from_user["id"]
    add_chat_to_db(str(chat_id))
    args = get_arg(message) + " " + "song"
    if args.startswith(" "):
        await message.reply("Enter a song name. Check /help")
        return ""
    status = await message.reply("š š š šššš«šš”š¢š§š  š­š”š š¬šØš§š ... š¶ šš„ššš¬š ššš¢š­ ā³ļø ššØš« ššš° ššššØš§šš¬ [š](https://telegra.ph/file/67f41ae52a85dfc0551ae.mp4)")
    video_link = yt_search(args)
    if not video_link:
        await status.edit("āļø ššØš®š§š ššØš­š”š¢š§š . ššØš«š«š².\n\nšš«š² šš§šØš­š”šš« ššš²š°šØš«š¤ šš« ššš²šš šš©šš„š„ šš­ šš«šØš©šš«š„š².\n\nEg.`/song Faded`")
        return ""
    yt = YouTube(video_link)
    audio = yt.streams.filter(only_audio=True).first()
    try:
        download = audio.download(filename=f"{str(user_id)}")
    except Exception as ex:
        await status.edit("Failed to download song š¶")
        LOGGER.error(ex)
        return ""
    rename = os.rename(download, f"{str(user_id)}.mp3")
    await app.send_chat_action(message.chat.id, "upload_audio")
    await app.send_audio(
        chat_id=message.chat.id,
        audio=f"{str(user_id)}.mp3",
        duration=int(yt.length),
        title=str(yt.title),
        performer=str(yt.author),
        reply_to_message_id=message.message_id,
    )
    await status.delete()
    os.remove(f"{str(user_id)}.mp3")