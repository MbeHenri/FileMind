from PIL import Image
from PIL.ExifTags import TAGS as PIL_TAGS
from pydantic import BaseModel
from typing import Any, Dict, Optional
from .base import BaseMetadata, getBaseMetadata

from .utils import format_filesize, format_timestamp, join_sentences, shorten


class ImageMetadata(BaseModel):
    baseMetadata: BaseMetadata

    spatialFrequencyResponse: Optional[Any] = None
    subjectLocation: Optional[Any] = None
    exposureIndex: Optional[Any] = None
    cFAPattern: Optional[Any] = None
    flashEnergy: Optional[Any] = None
    tIFF_EPStandardID: Optional[Any] = None
    # Pour les autres tags, on peut ajouter un champ générique si besoin
    otherMetadata: Dict[str, Any] = {}


def getMetadataImageFile(pathfile: str) -> ImageMetadata:
    image = Image.open(pathfile)
    exif_data = image.getexif()
    metadata = {}
    for tag_id, value in exif_data.items():
        tag_name = PIL_TAGS.get(tag_id, tag_id)
        metadata[tag_name] = value

    # Construction du modèle avec les tags spécifiques
    return ImageMetadata(
        baseMetadata=getBaseMetadata(pathfile),
        spatialFrequencyResponse=metadata.get("SpatialFrequencyResponse"),
        subjectLocation=metadata.get("SubjectLocation"),
        exposureIndex=metadata.get("ExposureIndex"),
        cFAPattern=metadata.get("CFAPattern"),
        flashEnergy=metadata.get("FlashEnergy"),
        tIFF_EPStandardID=metadata.get("TIFF/EPStandardID"),
        otherMetadata={
            k: v
            for k, v in metadata.items()
            if k
            not in {
                "SpatialFrequencyResponse",
                "SubjectLocation",
                "ExposureIndex",
                "CFAPattern",
                "FlashEnergy",
                "TIFF/EPStandardID",
            }
        },
    )


def describeImage(
    metadata: ImageMetadata,
    contenu_textuel: Optional[str] = None,
    max_longueur_contenu: int = 600,
) -> str:
    parts = []

    # BaseMetadata
    if metadata.baseMetadata:
        parts.append(f"Fichier image")
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
        parts.append("Image (métadonnées de base indisponibles)")

    # Métadonnées techniques
    tech_info = []
    if metadata.spatialFrequencyResponse is not None:
        tech_info.append(
            f"réponse en fréquence spatiale : {metadata.spatialFrequencyResponse}"
        )
    if metadata.subjectLocation is not None:
        tech_info.append(f"localisation du sujet : {metadata.subjectLocation}")
    if metadata.exposureIndex is not None:
        tech_info.append(f"indice d'exposition : {metadata.exposureIndex}")
    if metadata.cFAPattern is not None:
        tech_info.append(f"motif CFA : {metadata.cFAPattern}")
    if metadata.flashEnergy is not None:
        tech_info.append(f"énergie du flash : {metadata.flashEnergy}")
    if metadata.tIFF_EPStandardID is not None:
        tech_info.append(f"ID TIFF/EP : {metadata.tIFF_EPStandardID}")
    if metadata.otherMetadata:
        for k, v in metadata.otherMetadata.items():
            tech_info.append(f"{k} : {v}")

    if tech_info:
        parts.append(" — ".join(tech_info))

    description = join_sentences(parts)
    if not description.endswith("."):
        description += "."

    # Contenu textuel (OCR, légende, description)
    if contenu_textuel and contenu_textuel.strip():
        extrait = shorten(contenu_textuel.replace("\n", " "), max_longueur_contenu)
        description += f" Contenu textuel : {extrait}"
        if not description.endswith(".") and not description.endswith("…"):
            description += "."

    return description
