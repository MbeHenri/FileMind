from PIL import Image
from PIL.ExifTags import TAGS


def getMetadataImageFile(pathfile: str):

    image = Image.open(pathfile)
    exif_data = image._getexif()
    metadata = {}
    if exif_data:
        for tag_id, value in exif_data.items():
            tag_name = TAGS.get(tag_id, tag_id)
            metadata[tag_name] = value

    return metadata
