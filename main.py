from telethon import events
from config import bot
from FastTelethon import download_file, upload_file
import time
import datetime as dt


class Timer:
    def __init__(self, time_between=2):
        self.start_time = time.time()
        self.time_between = time_between

    def can_send(self):
        if time.time() > (self.start_time + self.time_between):
            self.start_time = time.time()
            return True
        return False


@bot.on(events.NewMessage(pattern=("/start")))
async def start(event):
    await bot.send_message(event.chat_id, "Im Running")


@bot.on(events.NewMessage(pattern=("/rename")))
async def rename(event):
    name = event.raw_text.split()
    name.pop(0)
    name = " ".join(name)
    msg = await event.get_reply_message()
    reply = await bot.send_message(event.chat_id, "Downloading") 
    download_location = await Download(reply, msg)
    await Upload(event, reply, download_location, "thumb.png", name)
    await reply.delete()


async def Download(reply, msg):
    timer = Timer()

    async def progress_bar(downloaded_bytes, total_bytes):
        if timer.can_send():
            await reply.edit(f"Downloading... {human_readable_size(downloaded_bytes)}/{human_readable_size(total_bytes)}")
    file = msg.document
    filename = msg.file.name
    dir = f"downloads/"
    if not filename:
        filename = (
            "video_" + dt.now().isoformat("_", "seconds") + ".mp4"
                    )
    download_location = dir + filename
    with open(download_location, "wb") as f:
        await download_file(
            client=bot, 
            location=file, 
            out=f,
            progress_callback=progress_bar
        )
    await reply.edit("Finished downloading")
    return download_location
   

async def Upload(event, reply, file_location, thumbnail, name):
    timer = Timer()

    async def progress_bar(downloaded_bytes, total_bytes):
        if timer.can_send():
            await reply.edit(f"Uploading... {human_readable_size(downloaded_bytes)}/{human_readable_size(total_bytes)}")

    with open(file_location, "rb") as f:
        ok = await upload_file(
            client=bot,
            file=f,
            name=name,
            progress_callback=progress_bar
        )
    await bot.send_message(
        event.chat_id, file=ok,
        force_document=True,
        thumb=thumbnail
    )
 

def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024.0 or unit == 'PB':
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"


@bot.on(events.NewMessage(pattern=("/sthumb")))
async def thumb(event):
    x = await event.get_reply_message()
    thumb = await bot.download_media(x.photo)
    with open(thumb, "rb") as f:
        pic = f.read()
    with open("thumb.png", "wb") as f:
        f.write(pic)
    await event.reply("Set as default thumbnail")


@bot.on(events.NewMessage(pattern=("/cthumb")))
async def clear_thumb(event):
    with open("thumb.png", "w") as f:
        f.write("")
    await event.reply("cleared thumbnail")


@bot.on(events.NewMessage(pattern=("/vthumb")))
async def view(event):
    try:
        await event.reply("current default thumbnail", file="thumb.png")
    except:
        await event.reply("No default thumbnail set")


bot.start()

bot.run_until_disconnected()
