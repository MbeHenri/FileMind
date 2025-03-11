import os

from .utils.__ini__ import getMetadataFile


class Preprocessor:
    def __init__(self, path_dir: str, deep: bool = False):
        self.path_dir = path_dir
        self.deep = deep

    def getFiles(self, deep: bool | None = None):
        useDeep = deep if deep is not None else self.deep
        if useDeep:
            return self._get_deep_files()
        return self._get_plane_files()

    def _get_deep_files(self):

        files = []
        n = 0

        for root, _, filenames in os.walk(self.path_dir):
            for file in filenames:
                file_path = os.path.join(root, file)
                if os.path.isfile(file_path):
                    try:
                        metadata = getMetadataFile(file_path)
                        files.append({"file_path": file_path, "metadata": metadata})
                        n += 1
                    except Exception as e:
                        print(f"Error processing file {file_path}: {e}")

        return (files, n)

    def _get_plane_files(self):

        files = []
        n = 0

        for file in os.listdir(self.path_dir):
            file_path = os.path.join(self.path_dir, file)
            if os.path.isfile(file_path):
                try:
                    metadata = getMetadataFile(file_path)
                    files.append({"file_path": file_path, "metadata": metadata})
                    n += 1
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")

        return (files, n)
