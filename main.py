import os
import requests
import time

from dotenv import load_dotenv
from pytube import Search

import replicate

from moviepy.editor import AudioFileClip, ImageClip, TextClip, \
    CompositeVideoClip, concatenate_videoclips
from moviepy.config import change_settings

from PIL import Image
import numpy as np

from typing import List, Tuple, Optional


def create_gif_background(colors: List[Tuple[int, int, int]]) -> None:
    width, height = 720, 1280
    duration = 3

    n_frames = int(duration * 30)
    n_colors = len(colors)
    color_step = n_frames // (n_colors - 1)

    color_index = 0
    frames = []
    for i in range(n_frames):
        if i % color_step == 0 and color_index < n_colors - 1:
            start_color = colors[color_index]
            end_color = colors[color_index + 1]
            color_index += 1

        color = np.full((height, width, 3), start_color, dtype=np.uint8)
        for j in range(3):
            color[:, :, j] += (end_color[j] - start_color[j]) * \
                (i % color_step) // color_step
        frames.append(Image.fromarray(color))

    frames[0].save(f'{files_path}transicao.gif', format='GIF',
                   append_images=frames[1:], save_all=True,
                   duration=int(1000 / 30), loop=0)


def download_music(music_artist: str, music_name: str) -> None:
    try:
        search_query = Search(music_artist + ' ' + music_name)
        search_query = search_query.results[0]
        music = search_query.streams.filter(only_audio=True).first()
        downloaded_file = music.download(files_path)
        new_file = f'{files_path}music.mp3'
        os.rename(downloaded_file, new_file)
        print(f">>> The music {music_name.upper()} by '\
            f'{music_artist.upper()} was downloaded.")
    except Exception as err:
        print(f'">>> Error while download the music {music_name.upper()} '
              f'by {music_artist.upper()}.')
        print(">>> ", err)


def get_lyrics(music_artist: str, music_name: str,
               api_key: str, start_phrase: int = 0,
               qtd_phrases: int = 5) -> Optional[List[str]]:
    try:
        url = 'https://api.vagalume.com.br/search.php?art={0}&mus={1}'\
              '&apikey={2}'.format(music_artist, music_name, api_key)
        response = requests.get(url)

        if response.status_code == 200:
            json_data = response.json()
            if json_data['type'] == 'notfound':
                print(f'>>> Error while get the lyrics of the music '
                      f'{music_name.upper()} by {music_artist.upper()}.')
                return []
            music = json_data['mus'][0]['text']
            music = music.replace('\n\n', '\n')
            music = music.split('\n')[start_phrase: start_phrase + qtd_phrases]
            assert isinstance(music, list) and \
                all(isinstance(item, str) for item in music), \
                "Unexpected return type from get_lyrics()"
            print(f'>>> Get the lyrics of the music {music_name.upper()}'
                  f'by {music_artist.upper()}.')
            return music
        else:
            print(f'>>> Error while get the lyrics of the music'
                  f'{music_name.upper()} by {music_artist.upper()}.')
            return []
    except Exception as err:
        print(f'>>> Error while get the lyrics of the music '
              f'{music_name.upper()} by {music_artist.upper()}.')
        print('>>> ', err)
        return []


def generate_images(lyrics: list[str]) -> None:
    try:
        for idx, phrase in enumerate(lyrics):
            inputs = {
                'prompt': phrase,
                'image_dimensions': "768x768",
                'num_outputs': 1,
                'num_inference_steps': 50,
                'guidance_scale': 7.5,
                'scheduler': "PNDM",
                'negative_prompt': 'text,phrases,words,Graffiti',
            }
            output = version.predict(**inputs)
            img_data = requests.get(output[0]).content
            with open(f'{files_path}/{idx}.jpg', 'wb') as handler:
                handler.write(img_data)
            print(f'>>> The image {idx}.jpg was generated.')
            time.sleep(2)
        print('>>> All images was generated.')
    except Exception as err:
        print('>>> Error while generate the images.')
        print('>>> ', err)


def create_video() -> None:
    audio = AudioFileClip(f'{files_path}/music.mp3') \
        .subclip(start_second, start_second + duration)

    concatenate_array = []

    for idx in range(len(lyrics)):
        duration_clip = duration / len(lyrics)
        try:
            image = ImageClip(f'{files_path}/{idx}.jpg') \
                .set_duration(duration_clip)
        except FileNotFoundError:
            image = ImageClip(f'{files_path}/{idx}.png') \
                .set_duration(duration_clip)
        text = TextClip(lyrics[idx], font="Amiri-bold", fontsize=35,
                        color='yellow').set_duration(duration_clip)

        text_col = text.on_color(size=(text.w + 10, text.h + 40),
                                 color=(0, 0, 0), pos=(6, 'center'),
                                 col_opacity=1)

        image_col = image.on_color(size=(image.w, image.h + text.h + 40),
                                   pos=(0, 0), color=(0, 0, 0),
                                   col_opacity=0.85)

        compose = CompositeVideoClip([image_col.set_pos((0, 0)),
                                      text_col.set_pos(('center', image.h))])
        concatenate_array.append(compose)

    video = concatenate_videoclips(concatenate_array)
    video.audio = audio

    # video.preview()
    video.write_videofile(f'{files_path}output.mp4', fps=24,
                          codec='mpeg4', threads=1)


if __name__ == '__main__':

    # User Settings
    watermark = "@riveclips"
    artist = "Ice Cube"
    music = "It Was A Good Day"
    files_path = "assets/"
    first_phrase = 0
    qtd_phrases = 8
    start_second = 33
    duration = 25
    use_watermark = False
    lyrics = ['']

    # Environment Settings
    load_dotenv()
    change_settings({"IMAGEMAGICK_BINARY": os.getenv("magickPath")})
    vagalume_api_key = os.getenv("vagalumeKey")
    hugginface_api_key = os.getenv('hugginfaceKey')
    replicate_key = os.getenv('replicateKey')
    replicate_client = replicate.Client(api_token=replicate_key)
    model = replicate_client.models.get(os.getenv('modelName'))
    version = model.versions.get(os.getenv('modelIDVersion'))

    create_gif_background([(255, 0, 0), (0, 255, 0), (0, 0, 255)])
    # download_music(artist, music)
    # lyrics = get_lyrics(artist, music, vagalume_api_key,
    #                     first_phrase, qtd_phrases)
    # generate_images(lyrics)
    # for i in lyrics:
    #     print(i)
    # create_video()
