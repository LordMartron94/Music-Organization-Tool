from pathlib import Path
from typing import Dict, List

from py_common.logging import HoornLogger

from src.downloading.download_model import DownloadModel
from src.handlers.library_file_handler import LibraryFileHandler
from src.metadata.clear_metadata import ClearMetadata
from src.metadata.metadata_manipulator import MetadataManipulator, MetadataKey
from src.metadata.metadata_populater import MetadataPopulater


class MetadataAPI:
	"""Facade class for manipulating music metadata."""

	def __init__(self, logger: HoornLogger):
		self._logger = logger
		self._metadata_clear_tool: ClearMetadata = ClearMetadata(logger)
		self._metadata_manipulator: MetadataManipulator = MetadataManipulator(logger)
		self._musicbrainz_metadata_populater: MetadataPopulater = MetadataPopulater(logger)
		self._library_file_handler: LibraryFileHandler = LibraryFileHandler(logger)

	def clear_genres(self, music_directory: Path) -> None:
		self._metadata_clear_tool.clear_genres(music_directory)

	def clear_dates(self, music_directory: Path) -> None:
		self._metadata_clear_tool.clear_dates(music_directory)

	def update_metadata_from_dict(self, file_path: Path, metadata_dict: Dict[MetadataKey, str]) -> None:
		self._metadata_manipulator.update_metadata_from_dict(file_path, metadata_dict)

	def make_description_compatible(self, file_path: Path) -> None:
		self._metadata_manipulator.make_description_compatible(file_path)

	def make_description_compatible_for_library(self, directory_path: Path) -> None:
		music_files = self._library_file_handler.get_music_files(directory_path)
		for file_path in music_files:
			self._metadata_manipulator.make_description_compatible(file_path)

	def update_metadata(self, file_path: Path, metadata_key: MetadataKey, new_value: str) -> None:
		self._metadata_manipulator.update_metadata(file_path, metadata_key, new_value)

	def clear_metadata(self, file_path: Path, metadata_key: MetadataKey, empty_value: str) -> None:
		self._metadata_manipulator.clear_metadata(file_path, metadata_key, empty_value)

	def get_metadata(self, file_path: Path, metadata_key: MetadataKey) -> str:
		return self._metadata_manipulator.get_metadata(file_path, metadata_key)

	def get_all_metadata(self, file_path: Path) -> Dict[MetadataKey, str]:
		return self._metadata_manipulator.get_all_metadata(file_path)

	def get_metadata_keys(self, file_path: Path) -> List:
		return self._metadata_manipulator.get_metadata_keys(file_path)

	def populate_metadata_from_musicbrainz(self, directory_path: Path) -> None:
		self._musicbrainz_metadata_populater.find_and_embed_metadata(directory_path)

	def populate_metadata_from_musicbrainz_for_file(self, download_model: DownloadModel) -> None:
		self._musicbrainz_metadata_populater.find_and_embed_metadata_from_ids_for_file(download_model)

	def organize_music_files(self, directory_path: Path, organized_path: Path) -> None:
		self._library_file_handler.organize_music_files(directory_path, organized_path)

	def recheck_missing_metadata(self, organized_path: Path):
		self._library_file_handler.recheck_missing_metadata(organized_path)

	def rescan_entire_library(self, organized_path: Path):
		self._library_file_handler.rescan_entire_library(organized_path)

	def populate_metadata_from_musicbrainz_album(self, directory_path: Path, album_id: str):
		self._musicbrainz_metadata_populater.find_and_embed_metadata_from_album(directory_path, album_id)
