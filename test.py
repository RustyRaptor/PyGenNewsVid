import moviepy.editor as mpy
import gizeh as gz
from math import pi
import textwrap
import requests
from bs4 import BeautifulSoup
from gtts import gTTS
import os
import uuid
from datetime import datetime

vid_wid = 1920
vid_hig = 1080
primary_color = (77, 39, 36)
secondary_color = (59 / 255, 89 / 255, 152 / 255)
video_res = (vid_wid, vid_hig)

now = datetime.now()
date_time_str = now.strftime("%m%d%Y%H%M%S")

url_str = "https://www.telemundoarizona.com/noticias/mexico/sonora-un-campo-de-batalla-del-narco-en-el-desierto-entre-mexico-y-eeuu/2204540/"
page_obj = requests.get(url_str)

soup_obj = BeautifulSoup(page_obj.content, "html.parser")

headline_results = soup_obj.find(class_="article-headline")
headline_str = headline_results.text.strip()

body_results = soup_obj.find(class_="article-content")
body_elements = body_results.find_all("p")
body_str = ""
for i in body_elements:
    body_str = body_str + i.text.strip()

# Language in which you want to convert
tts_lang = "es"

# Passing the text and language to the engine,
# here we have marked slow=False. Which tells
# the module that the converted audio should
# have a high speed
tts_obj = gTTS(text=body_str, lang=tts_lang, slow=False)

# Saving the converted audio in a mp3 file named
# welcome
unique_filename = str(uuid.uuid4()) + date_time_str
audio_path_str = "audio/" + unique_filename + ".mp3"
tts_obj.save(audio_path_str)
audioclip = mpy.AudioFileClip(audio_path_str)

vid_duration = audioclip.duration


def render_text(t):
    surface = gz.Surface(vid_wid, vid_hig // 15, bg_color=primary_color)
    text = gz.text(
        headline_str,
        fontfamily="Charter",
        fontsize=vid_hig // 30,
        fontweight="bold",
        fill=secondary_color,
        xy=(vid_wid // 2, vid_hig // 30),
    )
    text.draw(surface)
    return surface.get_npimage()

def draw_stars(t):
    surface = gz.Surface(vid_wid, vid_hig // 15, bg_color=primary_color)
    for i in range(5):
        star = gz.star(
            nbranches=5,
            radius=vid_hig // 10 * 0.2,
            xy=[100 * (i + 1) + (vid_wid // 3), vid_hig // 20],
            fill=(0, 1, 0),
            angle=t * pi,
        )
        star.draw(surface)
    return surface.get_npimage()


video_text = mpy.VideoClip(render_text, duration=int(vid_duration))


cover_image_url = "https://www.nydailynews.com/resizer/O4zfEhzRPzDYFJJ28006ZE2l1w0=/800x532/top/arc-anglerfish-arc2-prod-tronc.s3.amazonaws.com/public/DQWUBFHAXM5KVESA5EE4I5VCWM.jpg"
video_cover_image = (
    mpy.ImageClip(cover_image_url).set_position(("center", 0)).resize(width=vid_wid / 3)
)

video_stars = mpy.VideoClip(draw_stars, duration=vid_duration)

final_video_noaudio = (
    mpy.CompositeVideoClip(
        [
            video_cover_image,
            video_text.set_position(("center", video_cover_image.size[1])),
            video_stars.set_position(("center", video_cover_image.size[1] + video_text.size[1])),
        ],
        size=video_res,
    )
    .on_color(color=primary_color, col_opacity=1)
    .set_duration(vid_duration)
)

final_video_withaudio = final_video_noaudio.set_audio(audioclip)

unique_filename = str(uuid.uuid4()) + date_time_str
video_path_str = "videos/" + unique_filename + ".mp4"
final_video_withaudio.write_videofile(video_path_str, fps=1)
