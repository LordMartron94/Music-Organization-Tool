from enum import Enum
from pathlib import Path
from typing import Dict, List

import mutagen
from py_common.logging import HoornLogger


class MetadataKey(Enum):
	Title = "title"

	Artist = "artist"
	Album = "album"
	AlbumArtist = "albumartist"

	Genre = "genre"
	Comments = "description"

	TrackNumber = "tracknumber"
	DiscNumber = "discnumber"
	Grouping = "grouping"

	Date = "date"
	Year = "year"

	Encoder = "encoder"
	Length = "length"


class MetadataManipulator:
	"""
	Class to help with music metadata manipulation.
	Relies on the mutagen library for reading and writing metadata.
	"""

	def __init__(self, logger: HoornLogger):
		self._logger: HoornLogger = logger

	def _load_file(self, file_path: Path) -> mutagen.File:
		try:
			return mutagen.File(str(file_path))
		except mutagen.MutagenError as e:
			self._logger.error(f"Error loading file {file_path}: {e}")
			return None

	def make_description_compatible(self, file_path: Path):
		self._logger.debug(f"Making description compatible for file {file_path.name}")

		file: mutagen.File = self._load_file(file_path)

		if file is None:
			return

		description_value = file.get(MetadataKey.Comments.value, "")
		file["comment"] = description_value
		file["comments"] = description_value

		file.save()

		self._logger.debug(f"Description compatible for file {file_path.name} - Done")

	def update_metadata_from_dict(self, file_path: Path, metadata_dict: Dict[MetadataKey, str]) -> None:
		file: mutagen.File = self._load_file(file_path)

		if file is None:
			return

		for key, value in metadata_dict.items():
			if key.value not in file.keys():
				self._logger.warning(f"Metadata key {key.value} not found in file {file_path} - Trying to Add it.")

			if key == MetadataKey.Comments:
				# Make compatible with other software that doesn't support the description field
				file["comment"] = value
				file["comments"] = [value]

			file[key.value] = value

		file.save()

	def update_metadata(self, file_path: Path, metadata_key: MetadataKey, new_value: str) -> None:
		file: mutagen.File = self._load_file(file_path)

		if metadata_key.value not in file.keys():
			self._logger.warning(f"Metadata key {metadata_key.value} not found in file {file_path}")

		file[metadata_key.value] = new_value
		file.save()

	def clear_metadata(self, file_path: Path, metadata_key: MetadataKey, empty_value: str) -> None:
		self.update_metadata(file_path, metadata_key, empty_value)

	def get_metadata(self, file_path: Path, metadata_key: MetadataKey) -> str:
		file: mutagen.File = self._load_file(file_path)

		if metadata_key.value not in file.keys():
			self._logger.warning(f"Metadata key {metadata_key.value} not found in file {file_path}")
			return ""

		return file[metadata_key.value]

	def get_all_metadata(self, file_path: Path) -> Dict[MetadataKey, str]:
		file: mutagen.File = self._load_file(file_path)
		if file is None:
			return {}

		metadata_dict: Dict[MetadataKey, str] = {}
		for key in MetadataKey:
			if key.value in file.keys():
				metadata_dict[key] = str(file[key.value][0])

		return metadata_dict

	def get_metadata_keys(self, file_path: Path) -> List:
		file: mutagen.File = self._load_file(file_path)
		if file is None:
			return []

		return file.keys()
