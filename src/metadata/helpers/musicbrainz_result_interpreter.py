import re
from typing import Dict, List, Callable

from py_common.logging import HoornLogger


class MusicBrainzResultInterpreter:
	"""Utility class to interpret MusicBrainz search results."""
	def __init__(self, logger: HoornLogger):
		self._logger = logger
		self._tests: List[Callable[[Dict, str], str or None]] = [
			self._exact_match,
			self._partial_match,
		]

	def choose_best_result(self, search_results, file_stem) -> str or None:
		"""
		Chooses the most likely recording ID from the search results based on simple heuristics.
		"""
		if not search_results['recording-list']:
			return None

		cleaned_file_stem = self._clean_string(file_stem)
		for test in self._tests:
			match = test(search_results, cleaned_file_stem)
			if match is not None:
				self._logger.debug(f"Best match found for {file_stem}: {match}")
				return match

		self._logger.debug(f"No best match found for {file_stem}, resorting to first result.")
		return search_results['recording-list'][0]['id']

	def _exact_match(self, search_results: Dict, file_stem: str) -> str or None:
		"""Checks if the recording title matches the given file stem exactly."""

		for recording in search_results['recording-list']:
			if recording['title'].lower() == file_stem.lower():
				return recording['id']

		return None

	def _partial_match(self, search_results: Dict, file_stem: str) -> str or None:
		"""Checks if the recording title partially matches the given file stem."""

		for recording in search_results['recording-list']:
			cleaned_recording_title = self._clean_string(recording['title'])
			if cleaned_recording_title in file_stem or file_stem in cleaned_recording_title:
				return recording['id']

		return None

	def _clean_string(self, text: str) -> str:
		"""
		Removes special characters and converts to lowercase for better matching.
		"""
		return re.sub(r'[^a-zA-Z0-9]', '', text.lower())

