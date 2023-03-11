import os

import requests
import torch
from diffusers import StableDiffusionPipeline
from dotenv import load_dotenv
from pytube import Search
from torch import autocast


def get_lyrics(music_artist: str, music_name: str, api_key: str) -> str:
    url = 'https://api.vagalume.com.br/search.php?art={0}&mus={1}&apikey={2}' \
        .format(music_artist, music_name, api_key)
    response = requests.get(url)

    if response.status_code == 200:
        json_data = response.json()
        music = json_data['mus'][0]['text']
        # music = music.replace('\n\n', '\n')
        print(music)
    else:
        print('Error.')


def download_music(music_artist: str, music_name: str) -> None:
    search_query = Search(music_artist + ' ' + music_name)
    search_query = search_query.results[0]
    music = search_query.streams.filter(only_audio=True).first()
    downloaded_file = music.download("temp/")
    base, _ = os.path.splitext(downloaded_file)
    new_file = base + '.mp3'
    os.rename(downloaded_file, new_file)
    print("Done")


def generate(text):
    with autocast(device):
        image = pipe(text, guidance_scale=8.5)["sample"][0]
    image.save('generatedimage.png')


if __name__ == '__main__':
    load_dotenv()
    artist = 'Lucy Rose'
    music = 'Middle of the Bed'
    api_key = os.getenv("vagalumeKey")
    hugginface_key = os.getenv('hugginfaceKey')

    # download_music(artist, music)
    # get_lyrics(artist, music, api_key)

    modelid = "CompVis/stable-diffusion-v1-4"
    device = "cuda"
    pipe = StableDiffusionPipeline.from_pretrained(
        modelid,
        revision="fp16",
        torch_dtype=torch.float16,
        use_auth_token=hugginface_key)
    pipe.to(device)

    generate('Dog and Cat')
