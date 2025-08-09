# from sentence_transformers import SentenceTransformer
import numpy as np, sqlite3
from pathlib import Path
from threading import Lock

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
SPACE = "sbert"


class EmbeddingModel:

    def __init__(self, model: str, model_name: str = MODEL_NAME, space: str = SPACE):
        self.model_name = model_name
        self.space = space

        # self.model = SentenceTransformer(model_name)
        self.model = model

    def getDimension(self):
        return 3

    def encode(self, text: str, normalize_embeddings=True):
        return np.array([[0.3, 0.3, 0.3]])

    def embed_text(self, text: str) -> np.ndarray:
        # avec normalisation L2
        v = self.model.encode(text, normalize_embeddings=True)
        return v.astype("float32")


def to_blob(vec: np.ndarray) -> bytes:
    return vec.astype("float32").tobytes()


def from_blob(b: bytes, dim: int) -> np.ndarray:
    return np.frombuffer(b, dtype="float32", count=dim)


class VectorStoreService:

    _instance = None
    # pour thread-safety
    _lock = Lock()

    def __init__(
        self, db_path: str = "app.db", model: EmbeddingModel = EmbeddingModel()
    ):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute(
            "PRAGMA journal_mode=WAL;"
        )  # mode WAL = perfs + accès concurrent

        # chargement du modele d'embeding
        self.model = model
        self.space = self.model.space
        self.dim = self.model.getDimension()

        # initialisation de la base de données
        self.execute(
            """
            -- vecteurs (un espace par type: 'sbert', 'clip', ...)
            CREATE TABLE IF NOT EXISTS vectors(
              id INTEGER PRIMARY KEY,
              path TEXT,
              space TEXT NOT NULL,         -- 'sbert'
              dim INTEGER NOT NULL,
              vec BLOB NOT NULL,           -- float32[] en BLOB
              UNIQUE(path, space)
            );
            """
        )

        self._initialized = True

    @classmethod
    def get_instance(cls, db_path: str = "app.db"):
        """
        Retourne l'unique instance de DatabaseService.
        La crée si elle n'existe pas encore.
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(db_path)
            return cls._instance

    def execute(self, sql: str, params: tuple = ()):
        """
        Exécute une requête SQL avec commit automatique.
        Retourne le curseur.
        """
        cur = self.conn.cursor()
        cur.execute(sql, params)
        self.conn.commit()
        return cur

    def upsertPath(self, path: Path, text: str):
        vec = self.model.embed_text(text).reshape(1, -1)

        # 1) miroir SQLite
        self.execute(
            """INSERT INTO vectors(path, space, dim, vec)
               VALUES(?,?,?,?)
               ON CONFLICT(path, space) DO UPDATE SET
                 vec=excluded.vec,
                 dim=excluded.dim;""",
            (str(path), self.space, self.dim, to_blob(vec[0])),
        )

    def deletePath(self, path: Path):
        # DB
        cur = self.execute(
            "SELECT id FROM vectors WHERE path=? AND space=?",
            (str(path), self.space),
        )
        row = cur.fetchone()
        if not row:
            return

        id = int(row[0])
        self.execute("DELETE FROM vectors WHERE id=?", (id,))

    def movePath(self, old: Path, new: Path):
        """
        Met à jour le chemin d'un fichier (cas de renommage/déplacement).
        """
        self.execute("UPDATE vectors SET path=? WHERE path=?;", (str(new), str(old)))
