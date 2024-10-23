from pathlib import Path
from typing import Optional

import pydantic


class DownloadModel(pydantic.BaseModel):
	"""Representation of a recording to download."""
	url: str
	path: Optional[Path] = None
	release_id: Optional[str] = None
	recording_id: Optional[str] = None
	genre: Optional[str] = None
	subgenre: Optional[str] = None
