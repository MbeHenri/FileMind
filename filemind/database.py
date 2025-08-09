import sqlite3
from pathlib import Path
from threading import Lock
from .extract.base import BaseMetadata


class DatabaseService:
    """
    Singleton pour gérer la connexion SQLite et exécuter des requêtes.
    Usage:
        db = DatabaseService.get_instance("app.db")
        db.execute("INSERT INTO ...", params)
    """

    _instance = None
    # pour thread-safety
    _lock = Lock()

    def __init__(self, db_path: str = "app.db"):
        if hasattr(self, "_initialized") and self._initialized:
            return
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute(
            "PRAGMA journal_mode=WAL;"
        )  # mode WAL = perfs + accès concurrent
        self.conn.execute("PRAGMA synchronous=NORMAL;")

        # initialisation de la base de données
        self.execute(
            """
            -- fichiers
            CREATE TABLE IF NOT EXISTS files(
              id INTEGER PRIMARY KEY,
              path TEXT UNIQUE,
              description TEXT,
              size INTEGER,
              createdAt INTEGER,
              updatedAt INTEGER,
              accessedAt INTEGER
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

    def query(self, sql: str, params: tuple = ()):
        """
        Exécute une requête SQL SELECT et retourne toutes les lignes.
        """
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()

    def close(self):
        """
        Ferme la connexion.
        """
        if self.conn:
            self.conn.close()
            self.conn = None

    def indexPath(self, path: Path, metadata: BaseMetadata, description: str = ""):
        """
        Insère ou met à jour un fichier dans la table 'files'.
        """
        self.execute(
            """INSERT INTO files(path,description,size,createdAt,updatedAt,accessedAt)
                   VALUES(?,?,?,?,?,?)
                   ON CONFLICT(path) DO UPDATE SET description=excluded.description,
                                                  size=excluded.size,
                                                  createdAt=excluded.createdAt,
                                                  updatedAt=excluded.updatedAt,
                                                  accessedAt=excluded.accessedAt;""",
            (
                str(path),
                description,
                metadata.fileSize,
                metadata.fileCreatedAt,
                metadata.fileUpdatedAt,
                metadata.fileAccessedAt,
            ),
        )

    def deletePath(self, path: Path):
        """
        Supprime un fichier de la table 'files' par son chemin.
        """

        self.execute("DELETE FROM files WHERE path = ?;", (str(path),))

    def movePath(self, old: Path, new: Path):
        """
        Met à jour le chemin d'un fichier (cas de renommage/déplacement).
        """
        self.execute("UPDATE files SET path=? WHERE path=?;", (str(new), str(old)))
