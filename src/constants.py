import os
from pathlib import Path
from typing import List

DOWNLOAD_PATH: Path = Path(os.path.realpath(__file__)).parent.parent.joinpath("downloads")
ORGANIZED_PATH: Path = Path("D:\\70 Music\\All Music")

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