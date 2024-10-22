from pathlib import Path

from py_common.logging import HoornLogger

from src.handlers.library_file_handler import LibraryFileHandler
from src.metadata.metadata_manipulator import MetadataManipulator, MetadataKey


class ClearMetadata:
	"""A tool to help clear metadata from music files."""
	def __init__(self, logger: HoornLogger):
		self._logger = logger
		self._library_helper: LibraryFileHandler = LibraryFileHandler(logger)
		self._metadata_helper: MetadataManipulator = MetadataManipulator(logger)

	def clear_genres(self, music_directory: Path):
		music_files = self._library_helper.get_music_files(music_directory)

		for music_file_path in music_files:
			self._logger.debug(f"Clearing genre from {music_file_path.stem}")
			self._metadata_helper.clear_metadata(music_file_path, MetadataKey.Genre, "No Genre")
			self._logger.info(f"Genre cleared from {music_file_path.stem}")

	def clear_dates(self, music_directory: Path):
		music_files = self._library_helper.get_music_files(music_directory)

		for music_file_path in music_files:
			self._logger.debug(f"Clearing dates from {music_file_path.stem}")
			self._metadata_helper.clear_metadata(music_file_path, MetadataKey.Date, "0000-00-00")
			self._logger.info(f"Dates cleared from {music_file_path.stem}")


