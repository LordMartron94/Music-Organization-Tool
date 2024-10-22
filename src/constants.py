import os
from pathlib import Path
from typing import List

ROOT: Path = Path(os.path.realpath(__file__)).parent.parent

DOWNLOAD_PATH: Path = ROOT.joinpath("downloads")
ORGANIZED_PATH: Path = Path("D:\\70 Music\\All Music")

DOWNLOAD_CHECKER_FILE: Path = ROOT.joinpath("downloads.txt")
COOKIES_FILE: Path = Path("D:\\.media\\.cookies\\cookies.txt")

SUPPORTED_MUSIC_EXTENSIONS: List[str] = [".mp3", ".wav", ".flac", ".m4a", ".ogg", ".wma", ".aiff", ".opus"]

GENRE_MAPPINGS: dict = {
	"christian music": {
		"label": "Christian Music",
		"main": True
	},
	"worship": {
		"label": "Worship & Praise",
		"main": False
	},
	"praise": {
		"label": "Worship & Praise",
		"main": False
	},
	"praise & worship": {
		"label": "Worship & Praise",
		"main": False
	},
	"hymns": {
		"label": "Hymns",
		"main": False
	}
}