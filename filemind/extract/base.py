import os
from typing import Optional
from pydantic import BaseModel

from .utils import format_filesize, format_timestamp, shorten


class BaseMetadata(BaseModel):
    fileCreatedAt: int
    fileUpdatedAt: int
    fileAccessedAt: int
    fileSize: int
    fileType: Optional[str] = None


def getBaseMetadata(pathfile: str) -> BaseMetadata:
    file_stat = os.stat(pathfile)
    return BaseMetadata(
        fileCreatedAt=int(file_stat.st_ctime),  # secondes (float)
        fileUpdatedAt=int(file_stat.st_mtime),
        fileAccessedAt=int(file_stat.st_atime),
        fileSize=int(file_stat.st_size),
    )


def describeGlobalFile(
    metadatas: BaseMetadata,
    contenu_contextuel: Optional[str] = None,
    max_longueur_contenu: int = 600,
) -> str:
    taille = format_filesize(metadatas.fileSize)
    date_creation = format_timestamp(metadatas.fileCreatedAt)
    date_modif = format_timestamp(metadatas.fileUpdatedAt)
    date_acces = format_timestamp(metadatas.fileAccessedAt)

    intro = (
        f"Le fichier « {metadatas.filename} » a une taille de {taille}. "
        f"Il a été créé le {date_creation}, modifié pour la dernière fois le {date_modif}, "
        f"et consulté en dernier le {date_acces}."
    )

    if contenu_contextuel and contenu_contextuel.strip():
        extrait = shorten(contenu_contextuel, max_longueur_contenu)
        # On évite le double point final si l’extrait se termine par ponctuation
        suffix = "" if extrait.endswith((".", "!", "?", "…")) else "."
        return f"{intro} Contexte : {extrait}{suffix}"

    return intro
