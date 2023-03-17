import os
import requests

from dotenv import load_dotenv
from pytube import Search

import replicate


def get_lyrics(music_artist: str, music_name: str, api_key: str) -> str:
    try:
        url = 'https://api.vagalume.com.br/search.php?art={0}&mus={1}&apikey={2}' \
            .format(music_artist, music_name, api_key)
        response = requests.get(url)

        if response.status_code == 200:
            json_data = response.json()
            music = json_data['mus'][0]['text']
            music = music.replace('\n\n', '\n')
            return music
            print(f'Get the lyrics of the music {music_name.upper()} by {music_artist.upper()}.')
            # print(music)
        else:
            print(f'Error while get the lyrics of the music {music_name.upper()} by {music_artist.upper()}.')
    except Exception as err:
        print(f'Error while get the lyrics of the music {music_name.upper()} by {music_artist.upper()}.')
        print(err)


def download_music(music_artist: str, music_name: str) -> None:
    try:
        search_query = Search(music_artist + ' ' + music_name)
        search_query = search_query.results[0]
        print('Downloading the music...', music)
        music = search_query.streams.filter(only_audio=True).first()
        downloaded_file = music.download(files_path)
        base, _ = os.path.splitext(downloaded_file)
        new_file = base + '.mp3'
        os.rename(downloaded_file, new_file)
        print(f"The music {music_name.upper()} by {music_artist.upper()} was downloaded.")
    except Exception as err:
        print(f'Error while download the music {music_name.upper()} by {music_artist.upper()}.')
        print(err)


def generate_images(lyrics:str) -> None:
    try:
        for idx, phrase in enumerate(lyrics.split('\n')):
            inputs = {
                'prompt': phrase,
                'image_dimensions': "768x768",
                'num_outputs': 1,
                'num_inference_steps': 50,
                'guidance_scale': 7.5,
                'scheduler': "DPMSolverMultistep",
            }
            output = version.predict(**inputs)
            img_data = requests.get(output[0]).content
            with open(f'{files_path}/{idx}.jpg', 'wb') as handler:
                handler.write(img_data)
            print(f'The image {idx}.jpg was generated.')
        print('All images was generated.')
    except Exception as err:
        print(f'Error while generate the images.')
        print(err)


if __name__ == '__main__':
    
    load_dotenv()
    artist = 'Adelle'
    music = 'Hello'
    vagalume_api_key = os.getenv("vagalumeKey")
    hugginface_api_key = os.getenv('hugginfaceKey')
    replicate_key = os.getenv('replicateKey')
    files_path = "temp/"

    download_music(artist, music)
    lyrics = get_lyrics(artist, music, vagalume_api_key)

    replicate_client = replicate.Client(api_token=replicate_key)
    model = replicate_client.models.get("stability-ai/stable-diffusion")
    version = model.versions.get("db21e45d3f7023abc2a46ee38a23973f6dce16bb082a930b0c49861f96d1e5bf")
    # generate_images(lyrics="A dog drinking a coffee\nA cat drinking a tea")