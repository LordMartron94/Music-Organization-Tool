import os
from pathlib import Path

DOWNLOAD_PATH: Path = Path(os.path.realpath(__file__)).parent.parent.joinpath("downloads")
ORGANIZED_PATH: Path = Path(os.path.realpath(__file__)).parent.parent.joinpath("organized")