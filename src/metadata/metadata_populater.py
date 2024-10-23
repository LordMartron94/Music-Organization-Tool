import re
from difflib import SequenceMatcher
from pathlib import Path
from pprint import pprint
from typing import List, Dict

import musicbrainzngs
from py_common.logging import HoornLogger

from src.downloading.download_model import DownloadModel
from src.handlers.library_file_handler import LibraryFileHandler
from src.metadata.helpers.musicbrainz_api_helper import MusicBrainzAPIHelper
from src.metadata.helpers.musicbrainz_result_interpreter import MusicBrainzResultInterpreter
from src.metadata.helpers.recording_model import RecordingModel
from src.metadata.metadata_manipulator import MetadataManipulator, MetadataKey


class MetadataPopulater:
	def __init__(self, logger: HoornLogger):
		self._logger = logger
		self._music_library_handler: LibraryFileHandler = LibraryFileHandler(logger)
		self._metadata_manipulator: MetadataManipulator = MetadataManipulator(logger)
		self._musicbrainz_interpreter: MusicBrainzResultInterpreter = MusicBrainzResultInterpreter(logger)
		self._recording_helper: MusicBrainzAPIHelper = MusicBrainzAPIHelper(logger)
		musicbrainzngs.set_useragent("Music Organization Tool", "0.0", "https://github.com/LordMartron94/music-organization-tool")

	def find_and_embed_metadata(self, directory_path: Path):
		"""
		Main function to find and embed metadata for all FLAC files in the download directory.
		"""
		self._logger.info("Starting metadata finder...")
		files: List[Path] = self._get_files(directory_path)
		for file in files:
			self._logger.info(f"Processing file: {file.name}")
			self._process_file(file)

	def find_and_embed_metadata_from_ids_for_file(self, download_model: DownloadModel) -> None:
		file_path = download_model.path
		recording_id = download_model.recording_id
		release_id = download_model.release_id
		genre = download_model.genre
		subgenres = download_model.subgenre

		recording_model: RecordingModel = self._recording_helper.get_recording_by_id(recording_id, release_id, genre=genre, subgenres=subgenres)

		if recording_model is None:
			return

		self._embed_metadata(file_path, recording_model)

	def find_and_embed_metadata_from_album(self, directory_path: Path, album_id: str):
		self._logger.info("Starting metadata finder...")
		files: List[Path] = self._get_files(directory_path)
		for file in files:
			self._logger.info(f"Processing file: {file.name}")
			self._process_file(file, album_id)

	def _process_file(self, file: Path, album_id: str = None) -> None:
		"""
		Processes a single music file to find and embed metadata.
		"""

		recording_model = self._find_recording(file, album_id)
		if recording_model:
			self._embed_metadata(file, recording_model)
		else:
			self._logger.warning(f"No metadata found for {file.name}")

	def _find_recording(self, file: Path, album_id: str = None) -> RecordingModel or None:
		"""
		Tries to find the MusicBrainz recording ID for the given file.
		Prompts the user for manual input or to skip if automatic search fails.
		"""

		if album_id is not None:
			album = musicbrainzngs.get_release_by_id(album_id, includes=["recordings"])
			recording_ids = [recording['recording']['id'] for recording in album['release']['medium-list'][0]['track-list']]
			models = [self._recording_helper.get_recording_by_id(recording_id, album_id) for recording_id in recording_ids]
			models = [model for model in models if model is not None]
			return self._choose_model(models, file)
		else:
			try:
				artist = input(f"Enter the author name for {file.stem}: ")

				search_results = self._search_musicbrainz(file.stem, artist)
				recording_id = self._musicbrainz_interpreter.choose_best_result(search_results, file.stem)
				recording_model: RecordingModel = self._recording_helper.get_recording_by_id(recording_id)
				return recording_model
			except musicbrainzngs.MusicBrainzError as e:
				self._logger.error(f"MusicBrainzError: {e}")

			manual = self._get_manual_mbid(file)
			if manual:
				return self._recording_helper.get_recording_by_id(manual)

			return None

	def _search_musicbrainz(self, recording: str, artist: str) -> dict:
		"""
		Searches MusicBrainz for recordings matching the given query.
		"""
		return musicbrainzngs.search_recordings(recording=recording, artist=artist)

	def _get_manual_mbid(self, file: Path) -> str or None:
		"""
		Prompts the user to enter the MusicBrainz ID manually or skip.
		"""
		while True:
			user_input = input(f"Could not find metadata for {file.name}. "
			                   "Enter MusicBrainz ID manually or 's' to skip: ")
			if user_input.lower() == 's':
				return None
			if self._is_valid_mbid(user_input):
				return user_input
			else:
				self._logger.error("Invalid MusicBrainz ID format.")

	def _is_valid_mbid(self, mbid: str) -> bool:
		"""
		Checks if the given string is a valid MusicBrainz ID format.
		"""
		pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
		return bool(re.match(pattern, mbid))

	def _embed_metadata(self, file: Path, recording_model: RecordingModel):
		"""
		Embeds as much metadata as possible from MusicBrainz into the FLAC file for Plexamp compatibility.
		"""
		try:
			self._metadata_manipulator.update_metadata_from_dict(file, recording_model.metadata)
			self._logger.info(f"Embedded metadata into {file.name}")
		except musicbrainzngs.MusicBrainzError as e:
			self._logger.error(f"MusicBrainzError: {e}")
		except Exception as e:
			self._logger.error(f"Error embedding metadata: {e}")

	def _get_files(self, directory_path: Path) -> List[Path]:
		return self._music_library_handler.get_music_files(directory_path)

	def _choose_model(self, models: List[RecordingModel], file: Path):
		ranked_models = self._rank_models_based_on_similarity_to_title(models, file.stem)
		return ranked_models[0]

	def _rank_models_based_on_similarity_to_title(self, models: List[RecordingModel], title: str) -> List[RecordingModel]:
		ranked_models = sorted(models, key=lambda model: self._similarity_score(model.metadata[MetadataKey.Title], title), reverse=True)
		return ranked_models

	def _similarity_score(self, title1: str, title2: str) -> float:
		matcher = SequenceMatcher(None, title1.lower(), title2.lower())
		return matcher.ratio()
