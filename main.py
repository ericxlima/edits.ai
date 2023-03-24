import os
import requests
import time
from typing import List, Optional, Any

import replicate
import numpy as np
from dotenv import load_dotenv
from pytube import Search
from PIL import Image

from moviepy.editor import AudioFileClip, ImageClip, TextClip, \
    CompositeVideoClip, concatenate_videoclips

from utils import generate_rgb_colors


class Movie:

    def __init__(self, music_name: str, music_artist: str,
                 path: str = 'assets/', first_verse: int = 0,
                 n_verses: int = 0, start_time: float = 0,
                 time_duration: float = 0, watermark: str = "",
                 use_background: bool = False, video_width: int = 720,
                 video_height: int = 1280, use_lyrics: bool = True) -> None:
        """Create a movie with the lyrics of a song.

        Args:
            music_name (str): music of name, the same name that is in the Valume API.
            music_artist (str): name of artist of the music.
            path (str, optional): Directory of all files. Defaults to 'assets/'.
            first_verse (int, optional): Index to the first verse to lyrics. 
                                         Defaults to 0.
            n_verses (int, optional): Number of Verses to lyrics. Defaults to 0.
            start_time (float, optional): Start of lyrics, in seconds. Defaults to 0.
            time_duration (float, optional): Duration of lyrics video. Defaults to 0.
            watermark (str, optional): Your personal watermark, if don't pass, 
                                       any watermark was passed. Defaults to "".
            use_background (bool, optional): If True, the background of the video is
                                             randomly generated. Defaults to False (Black).
            video_width (int, optional): Width of the video in px. Defaults to 720.
            video_height (int, optional): Height of the video in px. Defaults to 1280.
            use_lyrics (bool, optional): If True, the lyrics will be used. Defaults to True.
        """

        self._music_name = music_name
        self._music_artist = music_artist
        self._path = path
        self._first_verse = first_verse
        self._n_verses = n_verses
        self._start_time = start_time
        self._time_duration = time_duration
        self._watermark = watermark
        self._use_background = use_background
        self._video_width = video_width
        self._video_height = video_height
        self._use_lyrics = use_lyrics

        self.__vagalume_api_key: Optional[str] = None
        self._lyrics: Optional[List[str]] = None
        self.__versionAI: Any = None

        self.config()

    @property
    def music_name(self) -> str:
        return self._music_name

    @property
    def music_artist(self) -> str:
        return self._music_artist

    @property
    def path(self) -> str:
        return self._path

    @property
    def first_verse(self) -> int:
        return self._first_verse

    @property
    def n_verses(self) -> int:
        return self._n_verses

    @property
    def start_time(self) -> float:
        return self._start_time

    @property
    def time_duration(self) -> float:
        return self._time_duration

    @property
    def watermark(self) -> str:
        return self._watermark

    @property
    def use_background(self) -> bool:
        return self._use_background

    @property
    def video_width(self) -> int:
        return self._video_width

    @property
    def video_height(self) -> int:
        return self._video_height

    @property
    def use_lyrics(self) -> bool:
        return self._use_lyrics

    @property
    def lyrics(self) -> Optional[List[str]]:
        return self._lyrics

    def config(self) -> None:
        """
        Load the .env file, create directory for files and other configs.
        """
        load_dotenv()

        if not os.path.exists(self.path):
            os.mkdir(self.path)

        if self.use_background:
            if not os.path.exists(f"{self.path}transition.gif"):
                self.create_gif_background()

        if not os.path.exists(f"{self.path}music.mp3"):
            self.download_music()

        self.__vagalume_api_key = os.getenv('vagalumeKey')
        if os.path.exists(f"{self.path}lyrics.txt"):
            with open(f"{self.path}lyrics.txt", 'r') as file:
                self._lyrics = file.read().splitlines()
        else:
            self._lyrics = self.get_lyrics()

        replicate_key = os.getenv('replicateKey')
        replicate_client = replicate.Client(api_token=replicate_key)
        model = replicate_client.models.get(os.getenv('modelName'))
        self.__versionAI = model.versions.get(os.getenv('modelIDVersion'))

    def create_gif_background(self) -> None:
        """Create a gif file with a transition of random colors, and
        save in the path directory.
        """
        try:

            if not self.n_verses or not self.time_duration:
                print('>>> Duration and Number of Verser are needed')
                return

            duration = self.time_duration / self.n_verses
            colors = [generate_rgb_colors() for _ in range(self.n_verses)]
            n_frames = int(duration * 60)
            color_step = n_frames // (self.n_verses - 1)

            color_index = 0
            frames = []
            for i in range(n_frames):
                if i % color_step == 0 and color_index < self.n_verses - 1:
                    start_color = colors[color_index]
                    end_color = colors[color_index + 1]
                    color_index += 1
                color = np.full((self.video_height, self.video_width, 3),
                                start_color)
                news_start_color = np.array(start_color, dtype=np.int32)
                news_end_color = np.array(end_color, dtype=np.int32)
                for j in range(3):
                    color[:, :, j] += (news_end_color[j] - news_start_color[j]) * \
                        (i % color_step) // color_step
                    color[:, :, j] = np.clip(color[:, :, j], 0, 255)
                frames.append(Image.fromarray(color.astype(np.uint8)))
            frames[0].save(f'{self.path}transition.gif', format='GIF',
                           append_images=frames[1:], save_all=True,
                           duration=self.time_duration / self.n_verses, loop=0)
        except Exception as err:
            print('>>> An error occurred while generating the gif: '
                  f'\n>>> {err}')

    def download_music(self) -> None:
        """
        Get the music from youtube and save in the path directory.
        """
        try:
            search_query = Search(f'{self.music_artist} {self.music_name}')
            search_query = search_query.results[0]
            music = search_query.streams.filter(only_audio=True).first()
            downloaded_file = music.download(self.path)
            new_file = f'{self.path}music.mp3'
            os.rename(downloaded_file, new_file)
            print(f'>>> The music "{self.music_name}" by '
                  f'"{self.music_artist}" was downloaded.')
        except Exception as err:
            print(f'>>> Error while download the music "{self.music_name}" '
                  f'by "{self.music_artist}".\n>>> {err}')

    def get_lyrics(self) -> Optional[List[str]]:
        """Get the lyrics of the music from the Vagalume API.

        Returns:
            Optional[List[str]]: The lyrics of the music, in strings inside list.
        """
        try:
            url = 'https://api.vagalume.com.br/search.php?art={0}&mus={1}'\
                  '&apikey={2}'.format(self.music_artist, self.music_name,
                                       self.__vagalume_api_key)
            response = requests.get(url)

            if response.status_code == 200:
                json_data = response.json()
                if json_data['type'] == 'notfound':
                    print(f'>>> Error while get the lyrics of the music '
                          f'"{self.music_name}" by "{self.music_artist}".')
                    return []
                music = json_data['mus'][0]['text']
                music = music.replace('\n\n', '\n')
                music = music.split('\n')
                music = music[self.first_verse: self.first_verse + self.n_verses]
                assert isinstance(music, list) and \
                    all(isinstance(item, str) for item in music), \
                    "Unexpected return type from get_lyrics()"
                print(f'>>> Get the lyrics of the music "{self.music_name}"'
                      f'by "{self.music_artist}".')
                with open(f'{self.path}lyrics.txt', 'w') as file:
                    for string in music:
                        file.write(string + '\n')
                return music
            else:
                print(f'>>> Error while get the lyrics of the music'
                      f'"{self.music_name}" by "{self.music_artist}".')
                return []
        except Exception as err:
            print(f'>>> Error while get the lyrics of the music '
                  f'"{self.music_name}" by "{self.music_artist}".')
            print('>>> ', err)
            return []

    def generate_images(self) -> None:
        """
        Generate images with the each verse of lyrics of the music.
        """
        try:
            assert isinstance(self._lyrics, list) and \
                all(isinstance(item, str) for item in self._lyrics), \
                "Unexpected return type from generate_images()"
            for idx, phrase in enumerate(self._lyrics):
                inputs = {
                    'prompt': phrase,
                    'image_dimensions': "768x768",
                    'num_outputs': 1,
                    'num_inference_steps': 50,
                    'guidance_scale': 7.5,
                    'scheduler': "PNDM",
                    'negative_prompt': 'text,phrases,words,Graffiti',
                }
                output = self.__versionAI.predict(**inputs)
                img_data = requests.get(output[0]).content
                with open(f'{self.path}{idx}.jpg', 'wb') as handler:
                    handler.write(img_data)
                print(f'>>> The image {idx}.jpg was generated.')
                time.sleep(2)
            print('>>> All images was generated.')
        except Exception as err:
            print('>>> Error while generate the images.')
            print('>>> ', err)

    def create_video(self, ) -> None:
        """
        Gereate the video with the images and the music.
        """
        audio = AudioFileClip(f'{self.path}music.mp3') \
            .subclip(self.start_time, self.start_time + self.time_duration)

        concatenate_array = []
        for idx in range(self.n_verses):
            duration_clip = self.time_duration / self.n_verses

            extensions = ['jpg', 'png']
            image_paths = [f'{self.path}{idx}.{ext}' for ext in extensions]
            valid_image_paths = list(filter(os.path.exists, image_paths))
            if valid_image_paths:
                image = ImageClip(valid_image_paths[0]) \
                    .set_duration(duration_clip)
            else:
                print('>>> Error while create the video.')
                print(f'>>> The image with index "{idx}" was not found.')
                return

            assert isinstance(self.lyrics, list) and \
                all(isinstance(item, str) for item in self.lyrics), \
                "Unexpected return type from create_video()"

            text = TextClip(self.lyrics[idx], font="Amiri-bold", fontsize=35,
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
        video.write_videofile(f'{self.path}output.mp4', fps=24,
                              codec='mpeg4', threads=1)


if __name__ == '__main__':

    movie = Movie(music_name="It Was A Good Day",
                  music_artist="Ice Cube",
                  path="assets/",
                  first_verse=0,
                  n_verses=8,
                  start_time=33,
                  time_duration=25,
                  use_background=True,
                  )
    movie.create_video()
