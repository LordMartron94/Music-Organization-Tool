from typing import List, Optional

import pydantic

from src.genre_detection.standardization.genre_standard_model import GenreStandardModel


class GenreDataModel(pydantic.BaseModel):
	main_genre: GenreStandardModel
	sub_genres: Optional[List[GenreStandardModel]]
