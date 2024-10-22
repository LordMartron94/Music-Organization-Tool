from typing import List

from py_common.logging import HoornLogger

from src.metadata.helpers.recording_model import RecordingModel
from src.metadata.metadata_manipulator import MetadataManipulator, MetadataKey


class MissingMetadataFinder:
	""" Utility class to find music files with missing metadata."""

	def __init__(self, logger: HoornLogger):
		self._logger = logger
		self._metadata_helper: MetadataManipulator = MetadataManipulator(logger)

	def find_missing_metadata(self, music_files: List[RecordingModel]) -> List[RecordingModel]:
		missing_metadata_files = []

		for file in music_files:
			metadata = file.metadata

			title = metadata[MetadataKey.Title]
			artist = metadata[MetadataKey.Artist]
			release_date = metadata[MetadataKey.Date]
			genre = metadata[MetadataKey.Genre]
			track_number = metadata[MetadataKey.TrackNumber]

			checks = {
				"title": self._check_value(title),
                "artist": self._check_value(artist),
                "release_date": self._check_value(release_date, "0000-00-00"),
                "genre": self._check_value(genre, "No Genre"),
                "track_number": self._check_value(track_number, "0")
			}

			for key, check in checks.items():
				if check:
					self._logger.warning(f"Missing metadata for {file.path.stem}: {key}")
					missing_metadata_files.append(file)
					break

		return missing_metadata_files

	def _check_value(self, value, extra_check: str = None) -> bool:
		if value == "" or value is None or (extra_check and value == extra_check):
			return True

		return False
