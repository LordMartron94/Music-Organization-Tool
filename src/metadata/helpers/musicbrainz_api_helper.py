import time
from typing import Dict, Tuple, List

import musicbrainzngs
from py_common.logging import HoornLogger

from src.constants import GENRE_MAPPINGS
from src.metadata.helpers.recording_model import RecordingModel
from src.metadata.helpers.release_model import ReleaseModel
from src.metadata.metadata_manipulator import MetadataKey


class MusicBrainzAPIHelper:
	"""Helper class for interacting with MusicBrainz recording API."""

	def __init__(self, logger: HoornLogger):
		self._logger = logger
		musicbrainzngs.set_useragent("Music Organization Tool", "0.0", "https://github.com/LordMartron94/music-organization-tool")

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

				release: ReleaseModel = self.get_release_by_id(release_id, recording_id, subgenres)

				metadata[MetadataKey.Artist] = artist
				metadata[MetadataKey.Title] = title
				metadata[MetadataKey.Album] = release.metadata[MetadataKey.Album]
				metadata[MetadataKey.AlbumArtist] = release.metadata[MetadataKey.AlbumArtist]
				metadata[MetadataKey.TrackNumber] = release.metadata[MetadataKey.TrackNumber]
				metadata[MetadataKey.DiscNumber] = release.metadata[MetadataKey.DiscNumber]
				metadata[MetadataKey.Date] = release.metadata[MetadataKey.Date]
				metadata[MetadataKey.Year] = release.metadata[MetadataKey.Year]
				metadata[MetadataKey.Length] = str(recording_length / 1000)  # Convert milliseconds to seconds
				metadata[MetadataKey.Genre] = release.metadata[MetadataKey.Genre] if genre is None else genre
				metadata[MetadataKey.Comments] = release.metadata[MetadataKey.Comments]
				metadata[MetadataKey.Grouping] = "No Energy"

				return RecordingModel(mbid=recording_id, metadata=metadata)

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

	def get_release_by_id(self, release_id: str, recording_id: str, subgenres: str = None) -> ReleaseModel:
		release = musicbrainzngs.get_release_by_id(release_id, includes=['artist-credits', 'media', 'tags', 'release-groups', 'recordings'])['release']

		metadata: Dict[MetadataKey, str] = {}

		album = release['title']
		album_artist = release['artist-credit'][0]['artist']['name']
		track_number, disc_number = self._get_track_and_disc_number(release, recording_id)
		release_date = self._get_release_date(release)
		genres = self._get_genres(release)

		metadata[MetadataKey.Album] = album
		metadata[MetadataKey.AlbumArtist] = album_artist
		metadata[MetadataKey.TrackNumber] = str(track_number if track_number else 0)
		metadata[MetadataKey.DiscNumber] = str(disc_number if disc_number else 0)
		metadata[MetadataKey.Date] = release_date
		metadata[MetadataKey.Year] = release_date[:4]

		filtered_genres: Tuple[str, List[str]] = self._filter_genres(genres)
		metadata[MetadataKey.Genre] = filtered_genres[0]

		if subgenres is None:
			metadata[MetadataKey.Comments] = "Subgenres: " + self._convert_sub_genres_to_string(filtered_genres[1]) + " | Vibe: N/A"
		else: metadata[MetadataKey.Comments] = "Subgenres: " + subgenres + " | Vibe: N/A"

		release_model = ReleaseModel(mbid=release_id, metadata=metadata)
		return release_model

	def _filter_genres(self, genres: List[str]) -> Tuple[str, List[str]]:
		sub_genres = []

		main_genre = "Other Genre"

		for genre in genres:
			if genre == "Specify the genre of music":
				continue

			genre_info = self._get_genre_info(genre)

			if genre_info is None:
				continue

			if not genre_info["main"]:
				sub_genres.append(genre)
			else: main_genre = genre_info["label"]

		return main_genre, sub_genres

	def _convert_sub_genres_to_string(self, genres: List[str]) -> str:
		if genres is None or genres == []:
			return "N/A"

		normalized_genres = [self._normalize_genre(genre) for genre in genres]
		duplicate_removed_genres = []

		for genre in normalized_genres:
			if genre not in duplicate_removed_genres:
				duplicate_removed_genres.append(genre)

		return "; ".join(duplicate_removed_genres)

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

	def _get_genres(self, release: dict) -> List[str]:
		return [tag['name'] for tag in release.get('tag-list', [])]

	def _get_genre_info(self, genre: str) -> dict or None:
		for genre_key, info in GENRE_MAPPINGS.items():
			if genre_key.lower() == genre.lower():
				return info

		self._logger.warning(f"No genre mapping found for '{genre}'.")
		return None

	def _normalize_genre(self, genre: str) -> str:
		"""
		Maps a MusicBrainz genre to a standardized top-level genre.

		Args:
		  genre: The genre string from MusicBrainz.

		Returns:
		  The standardized genre string, or 'Other' if no mapping is found.
		"""

		return self._get_genre_info(genre)["label"]
