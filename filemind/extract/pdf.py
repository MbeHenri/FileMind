from pypdf import PdfReader
from pydantic import BaseModel
from typing import Optional
from .base import BaseMetadata, getBaseMetadata

from .utils import (
    format_filesize,
    join_sentences,
    format_timestamp,
    shorten,
)


class PdfMetadata(BaseModel):
    baseMetadata: BaseMetadata

    title: Optional[str]
    author: Optional[str]
    subject: Optional[str]
    creator: Optional[str]
    producer: Optional[str]


def getMetadataPdfFile(pathfile: str) -> PdfMetadata:
    reader = PdfReader(pathfile)
    metadata = reader.metadata

    if metadata is None:
        return PdfMetadata()

    return PdfMetadata(
        baseMetadata=getBaseMetadata(pathfile),
        title=metadata.title,
        author=metadata.author,
        subject=metadata.subject,
        creator=metadata.creator,
        producer=metadata.producer,
    )


def describePdf(
    metadata: PdfMetadata,
    contenu_textuel: Optional[str] = None,
    max_longueur_contenu: int = 600,
) -> str:
    parts = []

    # Infos de base
    if metadata.baseMetadata:
        parts.append(f"Fichier PDF")

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
        parts.append("Fichier PDF (métadonnées de base indisponibles)")

    # Métadonnées spécifiques PDF
    pdf_info = []
    if metadata.title:
        pdf_info.append(f"titre : « {metadata.title} »")
    if metadata.author:
        pdf_info.append(f"auteur : {metadata.author}")
    if metadata.subject:
        pdf_info.append(f"sujet : {metadata.subject}")
    if metadata.creator:
        pdf_info.append(f"créé avec : {metadata.creator}")
    if metadata.producer:
        pdf_info.append(f"producteur : {metadata.producer}")

    if pdf_info:
        parts.append(" — ".join(pdf_info))

    description = join_sentences(parts)
    if not description.endswith("."):
        description += "."

    # Contenu textuel (ex. résumé ou texte OCR)
    if contenu_textuel and contenu_textuel.strip():
        extrait = shorten(contenu_textuel.replace("\n", " "), max_longueur_contenu)
        description += f" Contenu textuel : {extrait}"
        if not description.endswith(".") and not description.endswith("…"):
            description += "."

    return description
