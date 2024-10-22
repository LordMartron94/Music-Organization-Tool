from pathlib import Path
from typing import List

from py_common.handlers import FileHandler
from py_common.logging import HoornLogger

from src.constants import SUPPORTED_MUSIC_EXTENSIONS


class LibraryFileHandler:
	"""Wrapper class around the low-level file handler for use with music libraries."""
	def __init__(self, logger: HoornLogger):
		self._logger = logger
		self._file_handler = FileHandler()

	def get_music_files(self, directory: Path) -> List[Path]:
		"""
        Returns a list of all music files in the specified directory.
        """
		files: List[Path] = []

		for extension in SUPPORTED_MUSIC_EXTENSIONS:
			self._logger.debug("Searching for files with extension '{}'.".format(extension))
			files.extend(self._file_handler.get_children_paths(directory, extension))

		return files
