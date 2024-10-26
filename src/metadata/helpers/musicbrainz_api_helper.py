import time
from typing import Dict, Tuple, List

import musicbrainzngs
from py_common.logging import HoornLogger

from src.genre_detection.genre_algorithm import GenreAlgorithm
from src.genre_detection.model.genre_data_model import GenreDataModel
from src.metadata.helpers.recording_model import RecordingModel
from src.metadata.helpers.release_model import ReleaseModel
from src.metadata.metadata_manipulator import MetadataKey


class MusicBrainzAPIHelper:
	"""Helper class for interacting with MusicBrainz recording API."""

	def __init__(self, logger: HoornLogger, genre_algorithm: GenreAlgorithm):
		self._logger = logger
		musicbrainzngs.set_useragent("Music Organization Tool", "0.0", "https://github.com/LordMartron94/music-organization-tool")
		self._genre_algorithm = genre_algorithm

	def get_recording_by_id(self, recording_id: str, album_id: str = None, genre: str = None, subgenres: str = None) -> RecordingModel or None:
		self._logger.debug(f"Getting recording by ID: {recording_id}")
		metadata: Dict[MetadataKey, str] = {}

		retries = 3
		backoff_factor = 2
		for i in range(retries):
			try:
				recording = musicbrainzngs.get_recording_by_id(recording_id, includes=['artists', 'releases', 'tags'])

				title = recording['recording']['title']
				artist = recording['recording']['artist-credit'][0]['artist']['name']
				recording_length = int(recording['recording'].get('length', 0))  # in milliseconds

				# Get all releases for the recording
				releases = recording['recording']['release-list']

				# Let the user choose the correct release
				selected_release = self._choose_release(releases, artist, title) if album_id is None else None
				release_id = selected_release['id'] if selected_release is not None else album_id

				release: ReleaseModel = self.get_release_by_id(release_id, recording_id)

				metadata[MetadataKey.Artist] = artist
				metadata[MetadataKey.Title] = title
				metadata[MetadataKey.Album] = release.metadata[MetadataKey.Album]
				metadata[MetadataKey.AlbumArtist] = release.metadata[MetadataKey.AlbumArtist]
				metadata[MetadataKey.TrackNumber] = release.metadata[MetadataKey.TrackNumber]
				metadata[MetadataKey.DiscNumber] = release.metadata[MetadataKey.DiscNumber]
				metadata[MetadataKey.Date] = release.metadata[MetadataKey.Date]
				metadata[MetadataKey.Year] = release.metadata[MetadataKey.Year]
				metadata[MetadataKey.Length] = str(recording_length / 1000)  # Convert milliseconds to seconds
				metadata[MetadataKey.Grouping] = "No Energy"

				genre_data: GenreDataModel = self._genre_algorithm.get_genre_data(recording_id, release_id)

				main_genre = genre_data.main_genre.standardized_label
				sub_genres = [sub_genre.standardized_label for sub_genre in genre_data.sub_genres]

				metadata[MetadataKey.Genre] = main_genre if genre is None else genre
				metadata[MetadataKey.Comments] = "Subgenres: " + ("; ".join(sub_genres) if subgenres is None else subgenres)

				recording_model = RecordingModel(mbid=recording_id, metadata=metadata)
				recording_model.set_sub_genres(sub_genres)

				return recording_model

			except musicbrainzngs.WebServiceError as e:
				if e.cause.code in (429, 503):  # Rate limit error
					wait_time = backoff_factor ** i
					self._logger.warning(f"Rate limited, retrying in {wait_time} seconds...")
					time.sleep(wait_time)
				if e.cause.code == 400:
					self._logger.error(f"Bad request error: {e.message}")
					self._logger.error(f"Getting recording for recording id '{recording_id}' - release id '{album_id}'")
					return None
				else:
					raise

		self._logger.error(f"Failed to get recording after {retries} retries, skipping.")
		return None  # Or handle the failure appropriately

	def _choose_release(self, releases: List[dict], artist: str, title: str) -> dict:
		"""Prompts the user to select the correct release from a list."""
		self._logger.info(f"Found multiple releases for {artist} - {title}. Please choose the correct one:")
		for i, release in enumerate(releases):
			album_title = release.get('title', 'Unknown Album')
			release_date = release.get('date', 'Unknown Date')
			release_id = release['id']
			print(f"{i+1}. {album_title} ({release_date}) - MBID: {release_id}")

		while True:
			try:
				choice = int(input("Enter your choice: "))
				if 1 <= choice <= len(releases):
					return releases[choice - 1]
				else:
					print("Invalid choice. Please enter a number from the list.")
			except ValueError:
				print("Invalid input. Please enter a number.")

	def get_release_by_id(self, release_id: str, recording_id: str) -> ReleaseModel:
		self._logger.debug(f"Getting release by ID: {release_id}")
		release = musicbrainzngs.get_release_by_id(release_id, includes=['artist-credits', 'media', 'tags', 'release-groups', 'recordings'])['release']

		metadata: Dict[MetadataKey, str] = {}

		album = release['title']
		album_artist = release['artist-credit'][0]['artist']['name']
		track_number, disc_number = self._get_track_and_disc_number(release, recording_id)
		release_date = self._get_release_date(release)

		metadata[MetadataKey.Album] = album
		metadata[MetadataKey.AlbumArtist] = album_artist
		metadata[MetadataKey.TrackNumber] = str(track_number if track_number else 0)
		metadata[MetadataKey.DiscNumber] = str(disc_number if disc_number else 0)
		metadata[MetadataKey.Date] = release_date
		metadata[MetadataKey.Year] = release_date[:4]

		release_model = ReleaseModel(mbid=release_id, metadata=metadata)
		return release_model

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
		return release.get('date', "0000-00-00")
