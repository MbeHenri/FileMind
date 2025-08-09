# from __future__ import annotations
from watchdog.observers import Observer
from pathlib import Path
import queue, sys, time

from filemind.indexer import Indexer
from filemind.database import DatabaseService
from filemind.handler import Handler, Job, Worker, should_ignore
from filemind.vector_store import VectorStoreService

# chemin de la base SQLite
DB_PATH = "app.db"

VECTOR_STORE_PATH = "vector_store.db"

# nombre de threads pour traiter la file
WORKERS = 4


# -------------------- SCAN INITIAL --------------------
def scan(root: Path, file: queue.Queue[Job]):
    """
    Scanne tout un dossier au démarrage pour indexer les fichiers déjà présents.
    """
    for p in root.rglob("*"):
        if p.is_file() and not should_ignore(p):
            file.put(("created", p, {}))


# -------------------- LANCEUR PRINCIPAL --------------------
def run_watch(paths: list[str]):

    # files des fichiers a gerer
    qjobs: queue.Queue[Job] = queue.Queue(maxsize=10000)

    # service de la base de donnees
    db = DatabaseService.get_instance(db_path=DB_PATH)

    # service de stockage de vecteurs
    vector_store = VectorStoreService.get_instance(db_path=VECTOR_STORE_PATH)

    # l'indexateur de fichier
    indexer = Indexer(db, vector_store)

    # Lance les threads de traitement
    workers = [Worker(qjobs, indexer, name=f"worker-{i}") for i in range(WORKERS)]
    for w in workers:
        w.start()

    # Scan initial (avant de démarrer la surveillance)
    for p in paths:
        scan(Path(p), qjobs)

    # Démarre l'observateur watchdog
    obs = Observer()
    handler = Handler(qjobs)
    for p in paths:
        obs.schedule(handler, p, recursive=True)
    obs.start()

    print("[WATCHING]", ", ".join(paths))
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] waiting queue…")
        obs.stop()
        obs.join()
        qjobs.join()
        print("[BYE]")


if __name__ == "__main__":
    run_watch(sys.argv[1:] or ["./temp"])
