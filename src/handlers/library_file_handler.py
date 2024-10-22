from pathlib import Path
from typing import List

from py_common.handlers import FileHandler
from py_common.logging import HoornLogger

from src.constants import SUPPORTED_MUSIC_EXTENSIONS
from src.metadata.helpers.recording_model import RecordingModel
from src.metadata.metadata_manipulator import MetadataKey, MetadataManipulator
from src.metadata.missing_metadata_finder import MissingMetadataFinder


class LibraryFileHandler:
	"""Wrapper class around the low-level file handler for use with music libraries."""
	def __init__(self, logger: HoornLogger):
		self._logger = logger
		self._file_handler = FileHandler()
		self._metadata_manipulator = MetadataManipulator(logger)
		self._missing_metadata_finder: MissingMetadataFinder = MissingMetadataFinder(logger)

	def get_music_files(self, directory: Path) -> List[Path]:
		"""
        Returns a list of all music files in the specified directory.
        """
		files: List[Path] = []

		for extension in SUPPORTED_MUSIC_EXTENSIONS:
			self._logger.debug("Searching for files with extension '{}'.".format(extension))
			files.extend(self._file_handler.get_children_paths(directory, extension, recursive=True))

		return files

	def organize_music_files(self, directory_path: Path, organized_path: Path):
		"""
        Organizes the given music files into the specified organized_path.
        """
		all_files = [RecordingModel(metadata=self._metadata_manipulator.get_all_metadata(file), path=file) for file in self.get_music_files(directory_path)]
		missing_metadata_files = self._missing_metadata_finder.find_missing_metadata(all_files)
		correct_metadata_files = [file for file in all_files if file not in missing_metadata_files]

		for file in correct_metadata_files:
			self._place_accurate_file(file.path, file, organized_path)

		for file in missing_metadata_files:
			self._place_inaccurate_file(file.path, organized_path)

	def _place_accurate_file(self, file: Path, recording_model: RecordingModel, organized_path: Path) -> None:
		"""
		Places a music file into an organized directory structure based on its metadata.

		Args:
			file (Path): The path to the music file.
			recording_model (RecordingModel): The metadata associated with the recording.
			organized_path (Path): The root path of the organized music library.
		"""

		metadata = recording_model.metadata

		# Construct the new file name
		track_number = int(metadata[MetadataKey.TrackNumber])
		artist = metadata[MetadataKey.Artist]
		title = metadata[MetadataKey.Title]
		new_name = f"{track_number:02d} - {artist} - {title}{file.suffix.lower()}"

		# Construct the new directory path
		genre = metadata[MetadataKey.Genre].split(';')[0]
		album = metadata[MetadataKey.Album].replace("/", "-").replace(":", "_")
		new_path = organized_path / "SORTED" / genre / album / new_name

		# Create the directory structure if it doesn't exist
		new_path.parent.mkdir(parents=True, exist_ok=True)

		# Move and rename the file
		file.rename(new_path)
		self._logger.info(f"Moved '{file.name}' to '{new_path.parent.name}/{new_path.name}'")

	def _place_inaccurate_file(self, file: Path, organized_path: Path) -> None:
		new_path: Path = organized_path.joinpath("_MISSING METADATA").joinpath(file.name)

		# Make directories if necessary
		new_path.parent.mkdir(parents=True, exist_ok=True)

		file.rename(new_path)
		self._logger.info(f"Moved {file.name} to {new_path.parent.name}/{new_path.name}")

	def recheck_missing_metadata(self, organized_path: Path):
		self.organize_music_files(organized_path.joinpath("_MISSING METADATA"), organized_path)

	def rescan_entire_library(self, organized_path):
		self.organize_music_files(organized_path, organized_path)
