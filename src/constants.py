import os
from pathlib import Path
from typing import List

DOWNLOAD_PATH: Path = Path(os.path.realpath(__file__)).parent.parent.joinpath("downloads")
ORGANIZED_PATH: Path = Path(os.path.realpath(__file__)).parent.parent.joinpath("organized")

SUPPORTED_MUSIC_EXTENSIONS: List[str] = [".mp3", ".wav", ".flac", ".m4a", ".ogg", ".wma", ".aiff", ".opus"]