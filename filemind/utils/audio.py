import os
from tinytag import TinyTag


def getMetadataAudioFile(pathfile: str):

    audio_file = "/home/mbe/Documents/Fraudzen.aac"
    audio = TinyTag.get(audio_file)

    metadata = {
        "Title": audio.title,
        "Artist": audio.artist,
        "Genre": audio.genre,
        "Year Released": audio.year,
        "Bitrate": f"{audio.bitrate} kBits/s",
        "Composer": audio.composer,
        "Filesize": f"{audio.filesize} bytes",
        "AlbumArtist": audio.albumartist,
        "Duration": f"{audio.duration} seconds",
        "TrackTotal": audio.track_total,
    }
    return metadata
