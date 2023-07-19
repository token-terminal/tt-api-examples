import json
from pathlib import Path


class SimpleJSONFileCache:
    """Simple file cache for storing API responses."""

    dirpath: Path
    cache: dict = {}

    def __init__(self, dirpath: Path):
        self.dirpath = dirpath
        self.dirpath.mkdir(parents=True, exist_ok=True)

    def __getitem__(self, key: str):
        key = self.sanitize(key)
        if key in self.cache:
            return self.cache[key]
        path = self.getpath(key)
        if not path.exists():
            return None
        with open(path, "r") as f:
            from_json = json.load(f)
            self.cache[key] = from_json
        return self.cache[key]

    def __setitem__(self, key, value):
        key = self.sanitize(key)
        path = self.getpath(key)
        path.parent.absolute().mkdir(parents=True, exist_ok=True)
        with open(path, "w+") as f:
            as_json = json.dumps(value)
            f.write(as_json)
        self.cache[key] = value

    def __contains__(self, key):
        key = self.sanitize(key)
        if key in self.cache:
            return True
        path = self.getpath(key)
        return path.exists()

    def getpath(self, key: str) -> Path:
        key = self.sanitize(key)
        path = self.dirpath.joinpath(f"{key}.json")
        return path

    def sanitize(self, key: str) -> str:
        while key.startswith("/"):
            key = key[1:]
        while key.endswith("/"):
            key = key[:-1]
        return key
