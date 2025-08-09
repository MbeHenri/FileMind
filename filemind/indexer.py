from .vector_store import VectorStoreService
from .extract import extractFile
from .database import DatabaseService
from pathlib import Path
import stat
import numpy as np


def is_regular(p: Path):
    """
    Verifie si un fichier est un régulier, sinon None.
    """
    try:
        st = p.stat()
        if not stat.S_ISREG(st.st_mode):
            return False
        return True
    except FileNotFoundError:
        return False


def to_blob(vec: np.ndarray) -> bytes:
    return vec.astype("float32").tobytes()


def from_blob(b: bytes, dim: int) -> np.ndarray:
    return np.frombuffer(b, dtype="float32", count=dim)


# -------------------- INDEXEUR DE FICHIER --------------------


class Indexer:
    """
    Classe qui encapsule les actions d'indexation/désindexation.
    Tu peux brancher ici extraction de texte, insertion FTS5, embeddings, etc.
    """

    def __init__(self, db: DatabaseService, vectorStore: VectorStoreService):
        self.db = db
        self.vectorStore = vectorStore

    def index_path(self, p: Path):

        # on regarde si le fichier est regulier
        if not is_regular(p):
            print("[ERROR-REGULAR]", p)
            return

        # on essaye l'extraction de la description et des metadonnees du fichier
        result = extractFile(p)
        if not result:
            print("[ERROR-EXTRACTION]", p)
            return

        metadata, description = result
        self.db.indexPath(p, metadata, description=description)

        # on ajoute le vecteur d'embedding dans la base de données
        self.vectorStore.upsertPath(p, description)

        print("[INDEXED]", p)

    def remove_path(self, p: Path):
        self.vectorStore.deletePath(p)
        self.db.deletePath(p)

        print("[REMOVED]", p)

    def move_path(self, old: Path, new: Path):
        self.vectorStore.movePath(old, new)
        self.db.movePath(old, new)

        print("[MOVED]", old, "->", new)
