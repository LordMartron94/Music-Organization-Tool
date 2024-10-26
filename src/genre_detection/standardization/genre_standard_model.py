from typing import List, Optional

import pydantic


class GenreStandardModel(pydantic.BaseModel):
	"""Representation of a standardized genre."""
	potential_names: List[str]
	standardized_label: str
	subgenres: Optional[List["GenreStandardModel"]] = []
	is_main: bool = False

	def add_sub_genre(self, subgenre: "GenreStandardModel") -> None:
		"""Add a subgenre to this genre."""
		if self.subgenres is None:
			self.subgenres = []

		self.subgenres.append(subgenre)

	def __str__(self) -> str:
		"""String representation of the genre."""
		return self.standardized_label

	def genre_fits_standardized(self, genre: str) -> bool:
		"""Check if a given genre fits this standardized genre."""
		return genre.lower() in [potential_name.lower() for potential_name in self.potential_names]

	def get_all_sub_genres(self) -> List["GenreStandardModel"]:
		"""
		Recursively get all subgenres of this genre.
		"""

		subgenres = []

		if self.subgenres:
			for subgenre in self.subgenres:
				subgenres.append(subgenre)
				subgenres.extend(subgenre.get_all_sub_genres())

		return subgenres
