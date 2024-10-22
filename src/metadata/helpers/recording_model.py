from typing import Dict

import pydantic

from src.metadata.metadata_manipulator import MetadataKey


class RecordingModel(pydantic.BaseModel):
	mbid: str
	metadata: Dict[MetadataKey, str]
