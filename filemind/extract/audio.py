from typing import List, Optional
from pydantic import BaseModel
from tinytag import TinyTag

from .base import BaseMetadata, getBaseMetadata
from .utils import (
    format_list,
    format_channels,
    format_duration,
    format_bitrate,
    format_samplerate,
    format_filesize,
    join_sentences,
    format_timestamp,
    shorten,
)


class AudioMetadata(BaseModel):
    baseMetadata: BaseMetadata

    filesize: Optional[int]
    duration: Optional[float]
    channels: Optional[int]
    bitrate: Optional[int]
    samplerate: Optional[int]
    artist: Optional[List[str]]
    album: Optional[List[str]]
    title: Optional[List[str]]
    track: Optional[int]
    genre: Optional[List[str]]
    year: Optional[List[str]]
    comment: Optional[List[str]]


def getMetadataAudioFile(pathfile: str) -> AudioMetadata:
    audio = TinyTag.get(pathfile)
    metadata = AudioMetadata(
        baseMetadata=getBaseMetadata(pathfile),
        filename=pathfile,
        filesize=int(audio.filesize) if audio.filesize else None,
        duration=audio.duration,
        channels=audio.channels if hasattr(audio, "channels") else None,
        bitrate=int(audio.bitrate) if audio.bitrate else None,
        samplerate=(
            int(audio.samplerate)
            if hasattr(audio, "samplerate") and audio.samplerate
            else None
        ),
        artist=[audio.artist] if audio.artist else None,
        album=[audio.album] if hasattr(audio, "album") and audio.album else None,
        title=[audio.title] if audio.title else None,
        track=int(audio.track) if audio.track else None,
        genre=[audio.genre] if audio.genre else None,
        year=[str(audio.year)] if audio.year else None,
        comment=(
            [audio.comment] if hasattr(audio, "comment") and audio.comment else None
        ),
    )
    return metadata


def describeAudio(
    metadata: AudioMetadata,
    contenu_textuel: Optional[str] = None,
    max_longueur_contenu: int = 600,
) -> str:
    titre = format_list(metadata.title)
    artistes = format_list(metadata.artist)
    album = format_list(metadata.album)
    annee = format_list(metadata.year)
    piste = str(metadata.track) if metadata.track else None
    genres = format_list(metadata.genre)
    commentaire = format_list(metadata.comment)

    dur = format_duration(metadata.duration)
    ch = format_channels(metadata.channels)
    br = format_bitrate(metadata.bitrate)
    sr = format_samplerate(metadata.samplerate)

    # Métadonnées fichier
    fs = (
        format_filesize(metadata.baseMetadata.fileSize)
        if metadata.baseMetadata
        else None
    )
    created = (
        format_timestamp(metadata.baseMetadata.fileCreatedAt)
        if metadata.baseMetadata
        else None
    )
    updated = (
        format_timestamp(metadata.baseMetadata.fileUpdatedAt)
        if metadata.baseMetadata
        else None
    )
    accessed = (
        format_timestamp(metadata.baseMetadata.fileAccessedAt)
        if metadata.baseMetadata
        else None
    )

    intro_parts = []
    if artistes and titre:
        intro_parts.append(f"« {titre} » par {artistes}")
    elif titre:
        intro_parts.append(f"« {titre} »")
    else:
        pass

    context_bits = []
    if album:
        context_bits.append(f"extrait de l'album {album}")
    if piste:
        context_bits.append(f"piste {piste}")
    if annee:
        context_bits.append(f"({annee})")
    if genres:
        context_bits.append(f"genre : {genres}")
    if context_bits:
        intro_parts.append(" ".join(context_bits))

    tech_bits = []
    if dur:
        tech_bits.append(dur)
    if fs:
        tech_bits.append(fs)
    if ch:
        tech_bits.append(ch)
    if br:
        tech_bits.append(br)
    if sr:
        tech_bits.append(sr)
    if tech_bits:
        intro_parts.append(" — ".join(tech_bits))

    # Dates
    date_bits = []
    if created:
        date_bits.append(f"créé le {created}")
    if updated:
        date_bits.append(f"modifié le {updated}")
    if accessed:
        date_bits.append(f"dernier accès le {accessed}")
    if date_bits:
        intro_parts.append(" ; ".join(date_bits))

    if commentaire:
        intro_parts.append(f"Note : {commentaire}.")

    description = join_sentences(intro_parts).strip()
    if not description.endswith("."):
        description += "."

    if contenu_textuel and contenu_textuel.strip():
        extrait = shorten(contenu_textuel.replace("\n", " "), max_longueur_contenu)
        description += f" Contenu textuel : {extrait}"
        if not description.endswith(".") and not description.endswith("…"):
            description += "."

    return description
