import os
from pathlib import Path
from typing import List

ROOT: Path = Path(os.path.realpath(__file__)).parent.parent

DOWNLOAD_PATH: Path = ROOT.joinpath("downloads")
ORGANIZED_PATH: Path = Path(r"\\185.47.134.244\Media Drive\Media Library\Music")

DOWNLOAD_CHECKER_FILE: Path = ROOT.joinpath("downloads.txt")
DOWNLOAD_CSV_FILE: Path = ROOT.joinpath("downloads.csv")

COOKIES_FILE: Path = Path("D:\\.media\\.cookies\\cookies.txt")

SUPPORTED_MUSIC_EXTENSIONS: List[str] = [".mp3", ".wav", ".flac", ".m4a", ".ogg", ".wma", ".aiff", ".opus"]

GENRE_MAPPINGS: dict = {
	"christian music": {
		"label": "Christian Music",
		"main": False
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
	},
	"reggae": {
		"label": "Reggae",
		"main": True
	},
	"electronic": {
		"label": "Electronic",
		"main": False
	},
}