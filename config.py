import json

with open("config.json", "r") as config_file:
    config = json.load(config_file)

TEXT_TYPES = config["types"]["textes"]
IMAGE_TYPES = config["types"]["images"]
AUDIO_TYPES = config["types"]["audios"]
VIDEO_TYPES = config["types"]["videos"]
