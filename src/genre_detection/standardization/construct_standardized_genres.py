from typing import List

from py_common.logging import HoornLogger

from src.genre_detection.standardization.genre_standard_model import GenreStandardModel


class ConstructStandardizedGenres:
	"""
	Tool to construct standardized genres from user-provided genres.
	"""
	def __init__(self, logger: HoornLogger):
		self._logger = logger

	def _add_standardized_genre(self, keys: List[str], label: str, subgenres=None, is_main: bool = False):
		if subgenres is None:
			subgenres = []
		return GenreStandardModel(potential_names=keys, standardized_label=label, subgenres=subgenres, is_main=is_main)

	def _christian(self, standardized_models: List[GenreStandardModel]):
		worship_and_praise = self._add_standardized_genre(
			["worship", "praise", "praise & worship"],
			"Worship & Praise",
		)
		hymns = self._add_standardized_genre(["hymns"], "Hymns")

		standardized_models.append(self._add_standardized_genre(["christian music", "ccm"], "Christian Music", [worship_and_praise, hymns], True))

	def _reggae(self, standardized_models: List[GenreStandardModel]):
		roots_reggae = self._add_standardized_genre(["roots reggae"], "Roots Reggae")
		conscious_reggae = self._add_standardized_genre(["conscious reggae"], "Conscious Reggae")
		ragga_reggae = self._add_standardized_genre(["ragga"], "Ragga Reggae")
		dancehall_reggae = self._add_standardized_genre(["dancehall"], "Dancehall Reggae")

		standardized_models.append(self._add_standardized_genre(["reggae"], "Reggae", [roots_reggae, conscious_reggae, ragga_reggae, dancehall_reggae], is_main=True))

	def _hiphop(self, standardized_models: List[GenreStandardModel]):
		conscious_hip_hop = self._add_standardized_genre(["conscious hip hop"], "Conscious Hip-Hop")
		standardized_models.append(self._add_standardized_genre(["Hip-Hop", "Hip Hop"], "Hip-Hop", [conscious_hip_hop], is_main=True))

	def construct(self) -> List[GenreStandardModel]:
		standardized_models = []

		self._logger.debug("Constructing standardized genres...")
		self._christian(standardized_models)
		self._reggae(standardized_models)
		self._hiphop(standardized_models)

		standardized_models.append(self._add_standardized_genre(["*"], "Unknown Genre/Subgenre"))

		return standardized_models
