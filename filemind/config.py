import json

path_config = "config.json"

with open(path_config, "r") as config_file:
    config = json.load(config_file)

TEXT_TYPES = config["types"]["textes"]
IMAGE_TYPES = config["types"]["images"]
AUDIO_TYPES = config["types"]["audios"]
VIDEO_TYPES = config["types"]["videos"]
DOCUMENT_TYPES = config["types"]["documents"]