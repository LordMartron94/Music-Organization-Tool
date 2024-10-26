from pathlib import Path
from typing import Dict, Optional, List

import pydantic

from src.metadata.metadata_manipulator import MetadataKey


class RecordingModel(pydantic.BaseModel):
	mbid: Optional[str] = None
	path: Optional[Path] = None
	metadata: Dict[MetadataKey, str]
	_sub_genres: Optional[List[str]] = None

	def set_sub_genres(self, sub_genres: List[str]) -> None:
		self._sub_genres = sub_genres

	def get_sub_genres(self) -> List[str] or None:
		return self._sub_genres
