import os
from typing import Optional

from moviepy.editor import VideoFileClip
from PIL import Image

from ...core.logger import logging
from ...core.managers import edit_or_reply
from ..tools import media_type
from .utils import runcmd

LOGS = logging.getLogger(__name__)


async def media_to_pic(event, reply, noedits=False):  # sourcery no-metrics
    mediatype = media_type(reply)
    if mediatype not in [
        "Photo",
        "Round Video",
        "Gif",
        "Sticker",
        "Video",
        "Voice",
        "Audio",
        "Document",
    ]:
        return event, None
    if not noedits:
        Meowevent = await edit_or_reply(
            event, "`Transfiguration Time! Converting to ....`"
        )

    else:
        Meowevent = event
    Meowmedia = None
    Meowfile = os.path.join("./temp/", "meme.png")
    if os.path.exists(Meowfile):
        os.remove(Meowfile)
    if mediatype == "Photo":
        Meowmedia = await reply.download_media(file="./temp")
        im = Image.open(Meowmedia)
        im.save(Meowfile)
    elif mediatype in ["Audio", "Voice"]:
        await event.client.download_media(reply, Meowfile, thumb=-1)
    elif mediatype == "Sticker":
        Meowmedia = await reply.download_media(file="./temp")
        if Meowmedia.endswith(".tgs"):
            Meowcmd = f"lottie_convert.py --frame 0 -if lottie -of png '{Meowmedia}' '{Meowfile}'"
            stdout, stderr = (await runcmd(Meowcmd))[:2]
            if stderr:
                LOGS.info(stdout + stderr)
        elif Meowmedia.endswith(".webp"):
            im = Image.open(Meowmedia)
            im.save(Meowfile)
    elif mediatype in ["Round Video", "Video", "Gif"]:
        await event.client.download_media(reply, Meowfile, thumb=-1)
        if not os.path.exists(Meowfile):
            Meowmedia = await reply.download_media(file="./temp")
            clip = VideoFileClip(media)
            try:
                clip = clip.save_frame(Meowfile, 0.1)
            except Exception:
                clip = clip.save_frame(Meowfile, 0)
    elif mediatype == "Document":
        mimetype = reply.document.mime_type
        mtype = mimetype.split("/")
        if mtype[0].lower() == "image":
            Meowmedia = await reply.download_media(file="./temp")
            im = Image.open(Meowmedia)
            im.save(Meowfile)
    if Meowmedia and os.path.lexists(Meowmedia):
        os.remove(Meowmedia)
    if os.path.lexists(Meowfile):
        return Meowevent, Meowfile, mediatype
    return Meowevent, None


async def take_screen_shot(
    video_file: str, duration: int, path: str = ""
) -> Optional[str]:
    thumb_image_path = path or os.path.join(
        "./temp/", f"{os.path.basename(video_file)}.jpg"
    )
    command = f"ffmpeg -ss {duration} -i '{video_file}' -vframes 1 '{thumb_image_path}'"
    err = (await runcmd(command))[1]
    if err:
        LOGS.error(err)
    return thumb_image_path if os.path.exists(thumb_image_path) else None
