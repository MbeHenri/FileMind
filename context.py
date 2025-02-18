import os
from PIL import Image
from config import TEXT_TYPES, AUDIO_TYPES, IMAGE_TYPES, VIDEO_TYPES


def getContextFile(pathfile: str):

    if not os.path.exists(pathfile):
        raise FileNotFoundError(f"No such file: '{pathfile}'")

    file_type, _ = os.path.splitext(pathfile)

    if file_type in TEXT_TYPES:
        return getContextTextFile(pathfile)

    elif file_type in IMAGE_TYPES:
        return getContextImageFile(pathfile)

    elif file_type in AUDIO_TYPES:
        return getContextAudioFile(pathfile)

    elif file_type in VIDEO_TYPES:
        return getContextVideoFile(pathfile)


def getContextTextFile(pathfile: str):

    with open(pathfile, "r") as file:
        content = file.read()

    return content


def getContextImageFile(pathfile: str):

    image = Image.open(pathfile)

    return image


def getContextAudioFile(pathfile: str):

    return pathfile


def getContextVideoFile(pathfile: str):

    return pathfile
