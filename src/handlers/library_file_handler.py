from pathlib import Path
from typing import List

from py_common.handlers import FileHandler
from py_common.logging import HoornLogger

from src.constants import SUPPORTED_MUSIC_EXTENSIONS
from src.metadata.helpers.recording_model import RecordingModel
from src.metadata.metadata_manipulator import MetadataKey, MetadataManipulator


class LibraryFileHandler:
	"""Wrapper class around the low-level file handler for use with music libraries."""
	def __init__(self, logger: HoornLogger):
		self._logger = logger
		self._file_handler = FileHandler()
		self._metadata_manipulator = MetadataManipulator(logger)

	def get_music_files(self, directory: Path) -> List[Path]:
		"""
        Returns a list of all music files in the specified directory.
        """
		files: List[Path] = []

		for extension in SUPPORTED_MUSIC_EXTENSIONS:
			self._logger.debug("Searching for files with extension '{}'.".format(extension))
			files.extend(self._file_handler.get_children_paths(directory, extension))

		return files

	def organize_music_files(self, directory_path: Path, organized_path: Path):
		"""
        Organizes the given music files into the specified organized_path.
        """
		files = self.get_music_files(directory_path)

		for file in files:
			recording_model = RecordingModel(metadata=self._metadata_manipulator.get_all_metadata(file))
			self._place_file_correctly(file, recording_model, organized_path)

	def _place_file_correctly(self, file: Path, recording_model: RecordingModel, organized_path: Path) -> None:
		metadata = recording_model.metadata

		new_name: str = f"{int(metadata[MetadataKey.TrackNumber]):02d} - {metadata[MetadataKey.Artist]} - {metadata[MetadataKey.Title]}" + file.suffix.lower()
		new_path: Path = organized_path.joinpath(metadata[MetadataKey.Genre].split(';')[0]).joinpath(metadata[MetadataKey.Album].replace("/", "-").replace(":", "_")).joinpath(new_name)

		# Make directories if necessary
		new_path.parent.mkdir(parents=True, exist_ok=True)

		file.rename(new_path)
		self._logger.info(f"Moved {file.name} to {new_path.parent.name}/{new_path.name}")
