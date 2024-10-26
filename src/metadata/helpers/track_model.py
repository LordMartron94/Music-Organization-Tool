import pydantic


class TrackModel(pydantic.BaseModel):
	title: str
	track_number: str
	mbid: str

