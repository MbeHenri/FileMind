import queue, threading, time
from pathlib import Path
from watchdog.events import FileSystemEventHandler, FileSystemEvent, FileMovedEvent
from .indexer import Indexer
from concurrent.futures import ThreadPoolExecutor

# délai anti-rafale en millisecondes
DEBOUNCE_MS = 400

# Job d'un fichier (type d'événement, chemin, données annexes)
Job = tuple[str, Path, dict]

# -------------------- ANTI-RAFALE (DEBOUNCE) --------------------


class Debouncer:
    """
    Empêche le traitement multiple d'un même fichier modifié rapidement à la suite.
    """

    def __init__(self, delay_ms=DEBOUNCE_MS):
        self.delay = delay_ms / 1000
        self.lock = threading.Lock()

        # tableau des derniers fichiers analysees
        # [chemin] => temps d'enregistrement
        self.last: dict[Path, float] = {}

    def accept(self, p: Path) -> bool:
        now = time.time()
        with self.lock:
            t = self.last.get(p, 0)
            if now - t < self.delay:
                self.last[p] = now
                return False
            self.last[p] = now
            return True


# -------------------- OBSERVEUR DE REPERTOIRE --------------------


def should_ignore(p: Path) -> bool:
    """
    Vérifie si un fichier doit être ignoré selon son nom ou son dossier.
    """
    name = p.name
    if any(tok in p.parts for tok in (".git", ".cache")):
        return True
    if name.startswith("~$"):
        return True
    if name.endswith((".swp", ".tmp")):
        return True
    if name in (".DS_Store", "Thumbs.db", "app.db"):
        return True
    return False


class Handler(FileSystemEventHandler):
    """
    Traduit les événements watchdog en jobs à mettre dans la file des fichiers à gérer.
    """

    def __init__(self, qjobs: queue.Queue[Job], debouncer: Debouncer = Debouncer()):
        self.qjobs = qjobs
        self.debouncer = debouncer

    def _enqueue(self, kind: str, path: Path, extra: dict = None):
        if should_ignore(path):
            return
        if kind in ("created", "modified"):
            if not self.debouncer.accept(path):
                return
        self.qjobs.put((kind, path, extra or {}))

    def on_created(self, e: FileSystemEvent):
        if not e.is_directory:
            self._enqueue("created", Path(e.src_path))

    def on_modified(self, e: FileSystemEvent):
        if not e.is_directory:
            self._enqueue("modified", Path(e.src_path))

    def on_deleted(self, e: FileSystemEvent):
        if not e.is_directory:
            self._enqueue("deleted", Path(e.src_path))

    def on_moved(self, e: FileMovedEvent):
        if not e.is_directory:
            self._enqueue(
                "moved",
                Path(e.dest_path),
                {"src": Path(e.src_path), "dst": Path(e.dest_path)},
            )


# -------------------- WORKER DE TRAITEMENT DE JOB --------------------
class Worker(threading.Thread):
    """
    Thread qui lit la file de fichiers a gerer et effectue les action a effectuer grace a l'indexeur de fichiers.
    """

    def __init__(self, qjobs: queue.Queue[Job], indexer: Indexer, *a, **kw):
        super().__init__(*a, **kw)
        self.qjobs = qjobs  # file de fichier
        self.indexer = indexer
        self.pool = ThreadPoolExecutor(max_workers=1)

    def run(self):
        while True:
            kind, path, extra = self.qjobs.get()
            try:
                if kind in ("created", "modified"):
                    if path.exists() and not should_ignore(path):
                        self.indexer.index_path(path)
                elif kind == "deleted":
                    self.indexer.remove_path(path)
                elif kind == "moved":
                    self.indexer.move_path(extra["src"], extra["dst"])
            except Exception as e:
                print("[ERROR]", kind, path, e)
            finally:
                self.qjobs.task_done()
