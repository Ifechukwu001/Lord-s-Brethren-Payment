from pathlib import Path
from functools import lru_cache
from decouple import config as decouple_config, RepositoryEnv, Config

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


@lru_cache
def get_config():
    if ENV_FILE.exists():
        return Config(RepositoryEnv(ENV_FILE))
    return decouple_config


config = get_config()
