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
import logging
import threading
import time



def process_video(
        url_str=None, vid_wid=1920, vid_hig=1080,
        primary_color=(77, 39, 36),
        secondary_color=(59/255, 89/255, 152/255),
        
        ):
        
        video_res = (vid_wid, vid_hig)

        now = datetime.now()
        date_time_str = now.strftime("%m%d%Y%H%M%S")

        page_obj = requests.get(url_str)


        soup_obj = BeautifulSoup(page_obj.content, "html.parser")
        # print(soup_obj)

        # article-hero-headline__htag
        # article-body__content
        # headline_results = soup_obj.find(class_="article-headline")
        headline_results = soup_obj.find(class_="article-hero-headline__htag")

        meta_results = soup_obj.find_all('meta')

        for tag in meta_results:
                if 'name' in tag.attrs.keys() and tag.attrs['name'].strip().lower() in ['twitter:image']:
                        print ('NAME    :',tag.attrs['name'].lower())
                        meta_results = tag
                        # print ('CONTENT :',tag.attrs['content'])
        headline_str = headline_results.text.strip()
        meta_str = meta_results.attrs['content']
        # print(meta_str)


        # body_results = soup_obj.find(class_="article-content")
        body_results = soup_obj.find(class_="article-body__content")
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

        cover_image_url = meta_str
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
        
        return video_path_str
        

narcos_url="https://www.telemundo.com/Narcotrafico"
url_str = "https://www.telemundo.com/shows/hoy-dia/narcotrafico/experta-revela-secretos-detras-de-la-mente-criminal-de-joaquin-el-chap-rcna16705"

url_str_lst = []

page_obj = requests.get(narcos_url)


soup_obj = BeautifulSoup(page_obj.content, "html.parser")

links_results = soup_obj.find_all('a')

url_indent_str = "/noticias/noticias-telemundo/narcotrafico/"

with open("link_logs.txt", "r") as file_object:
        lines = file_object.read()
        list_of_lines = lines.splitlines()

print(list_of_lines)

with open("link_logs.txt", "a+") as file_object:

        for tag in links_results:
                if 'href' in tag.attrs.keys() and url_indent_str in tag.attrs['href']:
                        if tag.attrs['href'] in list_of_lines:
                                continue
                        url_str_lst.append(tag.attrs['href'])
                        # Move read cursor to the start of file.
                        file_object.seek(0)
                        # If file is not empty then append '\n'
                        data = file_object.read(100)
                        if len(data) > 0 :
                                file_object.write("\n")
                        # Append text at the end of file
                        file_object.write(tag.attrs['href'])
                        links_results = tag
                        
url_str_set = set(url_str_lst)


# process_video(url_str=url_str)




def thread_function(url_str, number, total):

    logging.info("Thread %s of %s: starting", number, total)

    process_video(url_str=url_str)

    logging.info("Thread %s of %s: finishing", number, total)




format = "%(asctime)s: %(message)s"

logging.basicConfig(format=format, level=logging.INFO,

                datefmt="%H:%M:%S")


video_threads = []

file_object = open('log.txt', 'a')

for thrd_num, url_str in enumerate(url_str_set):
        video_threads.append(threading.Thread(target=thread_function, args=(url_str, thrd_num, len(url_str_set))))
        video_threads[thrd_num].start()

logging.info("Main    : wait for the thread to finish")

for i in video_threads:
        i.join()

logging.info("Main    : all done")
