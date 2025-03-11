import os
import time

from filemind.config import (
    TEXT_TYPES,
    AUDIO_TYPES,
    IMAGE_TYPES,
    VIDEO_TYPES,
    DOCUMENT_TYPES,
)
from .audio import getMetadataAudioFile
from .pdf import getMetadataPdfFile
from .video import getMetadataVideoFile
from .image import getMetadataImageFile


def getBaseMetadata(pathfile: str):
    file_stat = os.stat(pathfile)
    """ return {
        "fileCreatedAt": time.ctime(file_stat.st_ctime),
        "fileUpdatedAt": time.ctime(file_stat.st_mtime),
        "fileAccessedAt": time.ctime(file_stat.st_atime),
        "fileSize": file_stat.st_size,
    } """
    return {
        "fileCreatedAt": file_stat.st_ctime_ns,
        "fileUpdatedAt": file_stat.st_mtime_ns,
        "fileAccessedAt": file_stat.st_atime_ns,
        "fileSize": file_stat.st_size,
    }


def getMetadataFile(pathfile: str):

    if not os.path.exists(pathfile):
        return None

    _, file_type = os.path.splitext(pathfile)
    type = None

    base_metadatas = getBaseMetadata(pathfile)
    metadata = {}

    if file_type in TEXT_TYPES:
        type = "text"

    elif file_type in IMAGE_TYPES:
        metadata = getMetadataImageFile(pathfile)
        type = "image"

    elif file_type in AUDIO_TYPES:
        metadata = getMetadataAudioFile(pathfile)
        type = "audio"

    elif file_type in VIDEO_TYPES:
        metadata = getMetadataVideoFile(pathfile)
        type = "video"
    elif file_type in DOCUMENT_TYPES:

        if file_type == ".pdf":
            metadata = getMetadataPdfFile(pathfile)

        type = "document"

    base_metadatas.update(metadata)
    base_metadatas["fileType"] = type
    return base_metadatas
