from pytube import Search
import os


def download_music(music_name:str) -> None:
    search_query = Search(music_name)
    search_query = search_query.results[0]
    music = search_query.streams.filter(only_audio=True).first()
    downloaded_file = music.download()
    base, _ = os.path.splitext(downloaded_file)
    new_file = base + '.mp3'
    os.rename(downloaded_file, new_file)
    print("Done")


download_music('Lucy Rose - Middle of the Bed')
