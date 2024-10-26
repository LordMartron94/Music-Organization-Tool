import os
from pathlib import Path
from typing import List

ROOT: Path = Path(os.path.realpath(__file__)).parent.parent

DOWNLOAD_PATH: Path = ROOT.joinpath("downloads")
ORGANIZED_PATH: Path = Path(r"\\185.47.134.244\Media Drive\Media Library\Music")

DOWNLOAD_CSV_FILE: Path = ROOT.joinpath("downloads.csv")

COOKIES_FILE: Path = Path("D:\\.media\\.cookies\\cookies.txt")

SUPPORTED_MUSIC_EXTENSIONS: List[str] = [".mp3", ".wav", ".flac", ".m4a", ".ogg", ".wma", ".aiff", ".opus"]