from typing import Dict, Tuple, List

import musicbrainzngs
from py_common.logging import HoornLogger

from src.metadata.helpers.recording_model import RecordingModel
from src.metadata.helpers.release_model import ReleaseModel
from src.metadata.metadata_manipulator import MetadataKey


class MusicBrainzAPIHelper:
	"""Helper class for interacting with MusicBrainz recording API."""

	def __init__(self, logger: HoornLogger):
		self._logger = logger
		musicbrainzngs.set_useragent("Music Organization Tool", "0.0", "https://github.com/LordMartron94/music-organization-tool")

	def get_recording_by_id(self, recording_id: str) -> RecordingModel:
		self._logger.debug(f"Getting recording by ID: {recording_id}")
		metadata: Dict[MetadataKey, str] = {}

		recording = musicbrainzngs.get_recording_by_id(recording_id, includes=['artists', 'releases', 'tags'])

		title = recording['recording']['title']
		artist = recording['recording']['artist-credit'][0]['artist']['name']
		recording_length = int(recording['recording'].get('length', 0))  # in milliseconds
		release_id = recording['recording']['release-list'][0]['id']

		release: ReleaseModel = self.get_release_by_id(release_id, recording_id)

		metadata[MetadataKey.Artist] = artist
		metadata[MetadataKey.Title] = title
		metadata[MetadataKey.Album] = release.metadata[MetadataKey.Album]
		metadata[MetadataKey.AlbumArtist] = release.metadata[MetadataKey.AlbumArtist]
		metadata[MetadataKey.TrackNumber] = release.metadata[MetadataKey.TrackNumber]
		metadata[MetadataKey.DiscNumber] = release.metadata[MetadataKey.DiscNumber]
		metadata[MetadataKey.Date] = release.metadata[MetadataKey.Date]
		metadata[MetadataKey.Length] = str(recording_length / 1000)  # Convert milliseconds to seconds
		metadata[MetadataKey.Genre] = release.metadata[MetadataKey.Genre]

		return RecordingModel(mbid=recording_id, metadata=metadata)

	def get_release_by_id(self, release_id: str, recording_id) -> ReleaseModel:
		release = musicbrainzngs.get_release_by_id(release_id, includes=['artist-credits', 'media', 'tags', 'release-groups'])['release']

		metadata: Dict[MetadataKey, str] = {}

		album = release['title']
		album_artist = release['artist-credit'][0]['artist']['name']
		track_number, disc_number = self._get_track_and_disc_number(release, recording_id)
		release_date = self._get_release_date(release)
		genres = self._get_genres(release)

		metadata[MetadataKey.Album] = album
		metadata[MetadataKey.AlbumArtist] = album_artist
		metadata[MetadataKey.TrackNumber] = str(track_number if track_number else 1)
		metadata[MetadataKey.DiscNumber] = str(disc_number if disc_number else 1)
		metadata[MetadataKey.Date] = release_date
		metadata[MetadataKey.Genre] = self._convert_genres_to_string(self._filter_genres(genres))

		release_model = ReleaseModel(mbid=release_id, metadata=metadata)
		return release_model

	def _filter_genres(self, genres: List[str]) -> List[str]:
		edited_genres = []

		for genre in genres:
			if genre == "Specify the genre of music":
				continue
			edited_genres.append(genre)

		return edited_genres

	def _convert_genres_to_string(self, genres: List[str]) -> str:
		return "; ".join(genres)

	def _get_track_and_disc_number(self, release: dict, recording_id: str) -> Tuple[int, int]:
		track_number = None
		disc_number = None
		for medium in release['medium-list']:
			for track in medium['track-list']:
				if track['recording']['id'] == recording_id:
					track_number = track['position']
					disc_number = medium['position']
					break
			if track_number:
				break

		return track_number, disc_number

	def _get_release_date(self, release: dict) -> str or None:
		return release.get('date', None)

	def _get_genres(self, release: dict) -> List[str]:
		return [tag['name'] for tag in release.get('tag-list', [])]
