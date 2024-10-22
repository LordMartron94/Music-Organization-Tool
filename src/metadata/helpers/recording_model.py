from pathlib import Path
from typing import Dict, Optional

import pydantic

from src.metadata.metadata_manipulator import MetadataKey


class RecordingModel(pydantic.BaseModel):
	mbid: Optional[str] = None
	path: Optional[Path] = None
	metadata: Dict[MetadataKey, str]
