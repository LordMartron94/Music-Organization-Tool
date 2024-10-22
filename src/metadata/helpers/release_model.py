from typing import Dict

import pydantic

from src.metadata.metadata_manipulator import MetadataKey


class ReleaseModel(pydantic.BaseModel):
	mbid: str
	metadata: Dict[MetadataKey, str]