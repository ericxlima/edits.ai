import os
import requests
import time

from dotenv import load_dotenv
from pytube import Search

import replicate

from moviepy.editor import AudioFileClip, ImageClip, TextClip, CompositeVideoClip, concatenate_videoclips
from moviepy.config import change_settings


def download_music(music_artist: str, music_name: str) -> None:
    try:
        search_query = Search(music_artist + ' ' + music_name)
        search_query = search_query.results[0]
        music = search_query.streams.filter(only_audio=True).first()
        downloaded_file = music.download(files_path)
        new_file = f'{files_path}music.mp3'
        os.rename(downloaded_file, new_file)
        print(f">>> The music {music_name.upper()} by {music_artist.upper()} was downloaded.")
    except Exception as err:
        print(f'">>> Error while download the music {music_name.upper()} by {music_artist.upper()}.')
        print(">>> ", err)


def get_lyrics(music_artist: str, music_name: str, api_key: str, 
               start_phrase:int=0, qtd_phrases:int=5) -> list:
    try:
        url = 'https://api.vagalume.com.br/search.php?art={0}&mus={1}&apikey={2}' \
            .format(music_artist, music_name, api_key)
        response = requests.get(url)

        if response.status_code == 200:
            json_data = response.json()
            if json_data['type'] == 'notfound':
                print(f'>>> Error while get the lyrics of the music {music_name.upper()} by {music_artist.upper()}.')
                return None
            music = json_data['mus'][0]['text']
            music = music.replace('\n\n', '\n')
            music = music.split('\n')[start_phrase: start_phrase + qtd_phrases]
            print(f'>>> Get the lyrics of the music {music_name.upper()} by {music_artist.upper()}.')
            return music
        else:
            print(f'>>> Error while get the lyrics of the music {music_name.upper()} by {music_artist.upper()}.')
    except Exception as err:
        print(f'>>> Error while get the lyrics of the music {music_name.upper()} by {music_artist.upper()}.')
        print('>>> ', err)


def generate_images(lyrics:list[str]) -> None:
    try:
        for idx, phrase in enumerate(lyrics):
            inputs = {
                'prompt': phrase,
                'image_dimensions': "768x768",
                'num_outputs': 1,
                'num_inference_steps': 50,
                'guidance_scale': 7.5,
                'scheduler': "PNDM",
                'negative_prompt':'text,phrases,words,Graffiti',
            }
            output = version.predict(**inputs)
            img_data = requests.get(output[0]).content
            with open(f'{files_path}/{idx}.jpg', 'wb') as handler:
                handler.write(img_data)
            print(f'>>> The image {idx}.jpg was generated.')
            time.sleep(2)
        print('>>> All images was generated.')
    except Exception as err:
        print(f'>>> Error while generate the images.')
        print('>>> ', err)
        
        
def create_video():
    audio = AudioFileClip(f'{files_path}/music.mp3').subclip(start_second, start_second + duration)
    
    concatenate_array = []
    
    for idx in range(qtd_phrases):
        duration_clip = duration/qtd_phrases
        image = ImageClip(f'{files_path}/{idx}.jpg').set_duration(duration_clip)
        text = TextClip(lyrics[idx], fontsize=40, color='white').set_duration(duration_clip)
        compose = CompositeVideoClip([image, text.set_pos('center')], size=(768, 768))
        concatenate_array.append(compose)

    video = concatenate_videoclips(concatenate_array)
    video.audio = audio
    
    video.preview()
    # video.write_videofile(f'{files_path}/output.mp4', fps=24, codec='libx264', audio_codec='aac')
    
    

if __name__ == '__main__':
    
    # User Settings
    artist = "Coolio"
    music = "Gangsta's Paradise"
    files_path = "assets2/"
    first_phrase = 0
    qtd_phrases = 10
    start_second = 26
    duration = 30
    
    # Environment Settings
    load_dotenv()
    change_settings({"IMAGEMAGICK_BINARY": os.getenv("magickPath")})
    vagalume_api_key = os.getenv("vagalumeKey")
    hugginface_api_key = os.getenv('hugginfaceKey')
    replicate_key = os.getenv('replicateKey')
    replicate_client = replicate.Client(api_token=replicate_key)
    model = replicate_client.models.get(os.getenv('modelName'))
    version = model.versions.get(os.getenv('modelIDVersion'))

    # download_music(artist, music)
    lyrics = get_lyrics(artist, music, vagalume_api_key, first_phrase, qtd_phrases)
    # generate_images(lyrics)
    
    create_video()
