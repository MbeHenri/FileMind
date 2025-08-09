from pymediainfo import MediaInfo
from pydantic import BaseModel
from typing import Optional
from .base import BaseMetadata, getBaseMetadata

from .utils import (
    format_filesize,
    join_sentences,
    format_timestamp,
    shorten,
    format_duration,
)


class VideoMetadata(BaseModel):
    baseMetadata: BaseMetadata
    format: Optional[str]
    duration: Optional[int]
    width: Optional[int]
    height: Optional[int]
    fps: Optional[float]
    frameCount: Optional[int]
    scanType: Optional[str]
    language: Optional[str]


def getMetadataVideoFile(pathfile: str) -> VideoMetadata:
    media_info = MediaInfo.parse(pathfile)

    metadata = {}
    for track in media_info.tracks:
        if track.track_type == "Video":
            metadata["format"] = track.format
            metadata["duration"] = track.duration
            metadata["width"] = track.width
            metadata["height"] = track.height
            metadata["fps"] = track.frame_rate
            metadata["frameCount"] = track.frame_count
            metadata["scanType"] = track.scan_type
            metadata["language"] = track.language

    return VideoMetadata(**metadata, baseMetadata=getBaseMetadata(pathfile))


def describeVideo(
    metadata: VideoMetadata,
    contenu_textuel: Optional[str] = None,
    max_longueur_contenu: int = 600,
) -> str:
    parts = []

    # Infos de base
    if metadata.baseMetadata:
        parts.append(f"Fichier vidéo")

        taille = format_filesize(metadata.baseMetadata.fileSize)
        if taille:
            parts.append(f"taille {taille}")

        dates = []
        created = format_timestamp(metadata.baseMetadata.fileCreatedAt)
        updated = format_timestamp(metadata.baseMetadata.fileUpdatedAt)
        accessed = format_timestamp(metadata.baseMetadata.fileAccessedAt)
        if created:
            dates.append(f"créé le {created}")
        if updated:
            dates.append(f"modifié le {updated}")
        if accessed:
            dates.append(f"dernier accès le {accessed}")
        if dates:
            parts.append(" ; ".join(dates))
    else:
        parts.append("Fichier vidéo (métadonnées de base indisponibles)")

    # Infos techniques vidéo
    tech_info = []
    if metadata.format:
        tech_info.append(f"format : {metadata.format}")
    if metadata.duration:
        tech_info.append(f"durée : {format_duration(metadata.duration)}")
    if metadata.width and metadata.height:
        tech_info.append(f"résolution : {metadata.width}x{metadata.height}")
    if metadata.fps:
        tech_info.append(f"{metadata.fps:.2f} images/s")
    if metadata.frameCount:
        tech_info.append(f"nombre d'images : {metadata.frameCount}")
    if metadata.scanType:
        tech_info.append(f"type de balayage : {metadata.scanType}")
    if metadata.language:
        tech_info.append(f"langue : {metadata.language}")

    if tech_info:
        parts.append(" — ".join(tech_info))

    description = join_sentences(parts)
    if not description.endswith("."):
        description += "."

    # Contenu textuel (ex. résumé, transcription, description)
    if contenu_textuel and contenu_textuel.strip():
        extrait = shorten(contenu_textuel.replace("\n", " "), max_longueur_contenu)
        description += f" Contenu textuel : {extrait}"
        if not description.endswith(".") and not description.endswith("…"):
            description += "."

    return description
