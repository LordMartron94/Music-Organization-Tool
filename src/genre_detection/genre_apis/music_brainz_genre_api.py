from typing import List, Tuple

import musicbrainzngs
from py_common.logging import HoornLogger

from src.genre_detection.genre_apis.genre_api_interface import GenreAPIInterface
from src.genre_detection.model.genre_data_model import GenreDataModel
from src.genre_detection.standardization.construct_standardized_genres import ConstructStandardizedGenres
from src.genre_detection.standardization.genre_standard_model import GenreStandardModel


class MusicBrainzGenreAPI(GenreAPIInterface):
	"""
	API for querying MusicBrainz genre data.
	"""

	def __init__(self, logger: HoornLogger):
		self._logger = logger
		construct_standardized_genres: ConstructStandardizedGenres = ConstructStandardizedGenres(logger)
		self._standardized_genres = construct_standardized_genres.construct()
		self._standardized_genres = self._compile_list_of_standardized_genres()
		self._unknown_genre: GenreStandardModel = self._get_unknown_genre()
		super().__init__(is_child=True)

	def get_genre_data(self, track_title: str, track_artist: str = None, track_album: str = None, track_id: str = None, album_id: str = None) -> GenreDataModel:
		self._logger.debug(f"Fetching genre data for track: {track_title} by {track_artist} ({track_id})")

		if track_id is None:
			self._logger.error("MusicBrainz API requires track ID to fetch genre data.")
			return GenreDataModel(main_genre=self._unknown_genre.standardized_label)

		track_genre_data = self._get_genre_data_from_musicbrainz(track_id)
		track_genres_mapped = self._map_genres(track_genre_data)
		main_genre, sub_genres = self._extract_main_and_sub_genres(track_genres_mapped)

		return GenreDataModel(
			main_genre=main_genre,
			sub_genres=sub_genres
		)

	def _get_genre_data_from_musicbrainz(self, track_id: str) -> List[str]:
		recording = musicbrainzngs.get_recording_by_id(track_id, includes=["tags"])

		try:
			genres = recording["recording"]["tag-list"]
		except KeyError:
			self._logger.error("No genres found for track ID.")
			return []

		return [genre["name"] for genre in genres]

	def _map_genres(self, genres: List[str]) -> List[GenreStandardModel]:
		mapped_genres = []

		for genre in genres:
			mapped = self._map_genre(genre)
			mapped_genres.append(mapped)

		return mapped_genres

	def _map_genre(self, genre: str) -> GenreStandardModel:
		standardized_genre = self._find_standardized_genre_for_genre(genre)

		if standardized_genre is not None:
			return standardized_genre

		self._logger.warning(f"Could not map genre: {genre}")
		return self._unknown_genre

	def _find_standardized_genre_for_genre(self, genre: str) -> GenreStandardModel or None:
		for standardized_genre in self._standardized_genres:
			if self._check_if_match(genre, standardized_genre):
				self._logger.debug(f"Mapped genre: {genre} to {standardized_genre.standardized_label}")
				return standardized_genre

	def _check_if_match(self, genre: str, standardized_genre: GenreStandardModel) -> bool:
		if standardized_genre.genre_fits_standardized(genre):
			return True

		return False

	def _get_unknown_genre(self) -> GenreStandardModel:
		for standardized_genre in self._standardized_genres:
			if "*" in standardized_genre.potential_names:
				return standardized_genre

	def _extract_main_and_sub_genres(self, track_genres_mapped: List[GenreStandardModel]) -> Tuple[GenreStandardModel, List[GenreStandardModel]]:
		"""
		Extracts the main genre and a list of sub-genres from a list of GenreStandardModel objects.

		Args:
			track_genres_mapped (List[GenreStandardModel]): A list of GenreStandardModel objects.

		Returns:
			Tuple[GenreStandardModel, List[GenreStandardModel]]: A tuple containing the main genre and a list of sub-genres.
		"""

		raw_main_genres = self._extract_raw_main_genres(track_genres_mapped)
		raw_sub_genres = self._extract_raw_sub_genres(track_genres_mapped)

		return self._determine_final_genres(raw_main_genres, raw_sub_genres)

	def _extract_raw_main_genres(self, track_genres_mapped: List[GenreStandardModel]) -> List[GenreStandardModel]:
		"""
		Extracts all genres marked as main from the input list.
		"""

		raw_main_genres = []

		for genre in track_genres_mapped:
			if genre.is_main and genre not in raw_main_genres:
				self._logger.debug(f"Found main genre: {genre.standardized_label}")
				raw_main_genres.append(genre)
			else:
				self._logger.debug(f"Skipping non-main genre: {genre.standardized_label}")

		return raw_main_genres

	def _extract_raw_sub_genres(self, track_genres_mapped: List[GenreStandardModel]) -> List[GenreStandardModel]:
		"""
		Extracts all genres not marked as main from the input list.
		"""

		raw_sub_genres = []

		for genre in track_genres_mapped:
			if not genre.is_main and genre not in raw_sub_genres:
				self._logger.debug(f"Found sub-genre: {genre.standardized_label}")
				raw_sub_genres.append(genre)
			else:
				self._logger.debug(f"Skipping genre: {genre.standardized_label}")

		return raw_sub_genres


	def _determine_final_genres(self, raw_main_genres: List[GenreStandardModel], raw_sub_genres: List[GenreStandardModel]) -> Tuple[GenreStandardModel, List[GenreStandardModel]]:
		"""
		Determines the final main genre and sub-genres based on the extracted raw genres.
		Handles cases with no, one, or multiple main genres.
		"""
		final_sub_genres: List[GenreStandardModel] = []

		if len(raw_main_genres) == 0:
			self._logger.warning("No main genre found for track.")
			final_main_genre = self._unknown_genre
		elif len(raw_main_genres) > 1:
			self._logger.warning("Multiple main genres found for track. Choosing first known one, mapping others as sub-genre.")
			final_main_genre = self._get_first_known_genre(raw_main_genres)
			removed = raw_main_genres.copy()
			removed.remove(final_main_genre)
			final_sub_genres.extend(removed)
		else:
			final_main_genre = raw_main_genres[0]

		final_sub_genres.extend(raw_sub_genres)

		return final_main_genre, final_sub_genres

	def _get_first_known_genre(self, raw_main_genres: List[GenreStandardModel]) -> GenreStandardModel:
		for genre in raw_main_genres:
			if "*" not in genre.potential_names:
				return genre

	def _compile_list_of_standardized_genres(self) -> List[GenreStandardModel]:
		"""
		Transforms the standardized genre list into a compiled list of genres. This allows for faster lookups.
		What I mean is that all the genre's subgenres are added to the list.
		"""
		compiled = []

		for standardized_genre in self._standardized_genres:
			compiled.append(standardized_genre)
			compiled.extend(standardized_genre.get_all_sub_genres())

		return compiled
