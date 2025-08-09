import os

from filemind.config import (
    TEXT_TYPES,
    AUDIO_TYPES,
    IMAGE_TYPES,
    VIDEO_TYPES,
    DOCUMENT_TYPES,
)
from .base import getBaseMetadata, describeGlobalFile
from .audio import getMetadataAudioFile, describeAudio
from .pdf import getMetadataPdfFile, describePdf
from .video import getMetadataVideoFile, describeVideo
from .image import getMetadataImageFile, describeImage
from .utils import readContentFile
from pathlib import Path

LIMIT_LENGHT_DESCRIPTION = 600


def filetype(path: Path):
    """
    Determine the type of file based on its extension.
    """
    ext = path.suffix.lower()
    if ext in TEXT_TYPES:
        return "text"
    elif ext in IMAGE_TYPES:
        return "image"
    elif ext in AUDIO_TYPES:
        return "audio"
    elif ext in VIDEO_TYPES:
        return "video"
    elif ext in DOCUMENT_TYPES:
        if ext == ".pdf":
            return "pdf"
    return None


def getMetadataFile(pathfile: str):

    if not os.path.exists(pathfile):
        return None

    file_type = filetype(pathfile)
    if not file_type:
        return None

    base_metadatas = getBaseMetadata(pathfile)
    metadata = {}

    if file_type == "text":
        metadata = base_metadatas.model_dump()
        metadata["baseMetadata"] = None
        base_metadatas.fileType = "text"

    if file_type == "image":
        metadata = getMetadataImageFile(pathfile).model_dump()
        metadata["baseMetadata"] = None
        base_metadatas.fileType = "image"

    elif file_type == "audio":
        metadata = getMetadataAudioFile(pathfile).model_dump()
        metadata["baseMetadata"] = None
        base_metadatas.fileType = "audio"

    elif file_type == "video":
        metadata = getMetadataVideoFile(pathfile).model_dump()
        metadata["baseMetadata"] = None
        base_metadatas.fileType = "video"

    elif file_type == "pdf":
        metadata = getMetadataPdfFile(pathfile).model_dump()
        metadata["baseMetadata"] = None
        base_metadatas.fileType = "pdf"

    base_metadatas = base_metadatas.model_dump()
    base_metadatas.update(metadata)
    return base_metadatas


def extractFile(path: Path):
    """
    Extract base metadata and description from a file.
    """

    if not path.exists():
        return None

    file_type = filetype(path)
    if not file_type:
        return None

    if file_type == "text":
        metadata = getBaseMetadata(path)
        metadata.fileType = "text"
        description = describeGlobalFile(
            metadata, readContentFile(path), LIMIT_LENGHT_DESCRIPTION
        )

    if file_type == "image":
        res = getMetadataImageFile(path)
        description = describeImage(res, "", LIMIT_LENGHT_DESCRIPTION)
        metadata = res.baseMetadata.model_copy()
        metadata.fileType = "image"

    elif file_type == "audio":
        metadata = getMetadataAudioFile(path)
        description = describeAudio(metadata, "", LIMIT_LENGHT_DESCRIPTION)
        metadata = metadata.baseMetadata
        metadata.fileType = "audio"

    elif file_type == "video":
        metadata = getMetadataVideoFile(path)
        description = describeVideo(metadata, "", LIMIT_LENGHT_DESCRIPTION)
        metadata = metadata.baseMetadata
        metadata.fileType = "video"

    elif file_type == "pdf":
        metadata = getMetadataPdfFile(path)
        description = describePdf(metadata, "", LIMIT_LENGHT_DESCRIPTION)
        metadata = metadata.baseMetadata
        metadata.fileType = "pdf"
    else:
        return None

    return metadata, description
