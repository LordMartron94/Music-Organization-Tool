from pathlib import Path
from pprint import pprint
from typing import List, Tuple

from mutagen.flac import FLAC
from py_common.handlers import FileHandler
from py_common.logging import HoornLogger

import musicbrainzngs
import re

from src.constants import DOWNLOAD_PATH, ORGANIZED_PATH


class MetadataFinder:
	def __init__(self, logger: HoornLogger):
		self._logger = logger
		self._file_helper = FileHandler()
		musicbrainzngs.set_useragent("Music Organization Tool", "0.0", "https://github.com/LordMartron94/music-organization-tool")

	def find_and_embed_metadata(self):
		"""
		Main function to find and embed metadata for all FLAC files in the download directory.
		"""
		self._logger.info("Starting metadata finder...")
		files: List[Path] = self._get_files()
		for file in files:
			self._logger.info(f"Processing file: {file.name}")
			self._process_file(file)

	def _process_file(self, file: Path):
		"""
		Processes a single FLAC file to find and embed metadata.
		"""
		recording_id = self._find_recording_id(file)
		if recording_id:
			self._embed_metadata(file, recording_id)
		else:
			self._logger.warning(f"No metadata found for {file.name}")

	def _find_recording_id(self, file: Path) -> str or None:
		"""
		Tries to find the MusicBrainz recording ID for the given file.
		Prompts the user for manual input or to skip if automatic search fails.
		"""
		try:
			search_results = self._search_musicbrainz(file.stem)
			recording_id = self._choose_best_result(search_results, file.stem)
			if recording_id and self._confirm_recording(recording_id):
				return recording_id
		except musicbrainzngs.MusicBrainzError as e:
			self._logger.error(f"MusicBrainzError: {e}")

		return self._get_manual_mbid(file)

	def _search_musicbrainz(self, query: str) -> dict:
		"""
		Searches MusicBrainz for recordings matching the given query.
		"""
		return musicbrainzngs.search_recordings(recording=query)

	def _choose_best_result(self, search_results: dict, file_stem: str) -> str or None:
		"""
		Chooses the most likely recording ID from the search results based on simple heuristics.
		"""
		if not search_results['recording-list']:
			return None

		# 1. Exact match on recording title
		for recording in search_results['recording-list']:
			if recording['title'].lower() == file_stem.lower():
				return recording['id']

		# 2. Partial match on recording title (ignoring special characters and case)
		cleaned_file_stem = self._clean_string(file_stem)
		for recording in search_results['recording-list']:
			cleaned_recording_title = self._clean_string(recording['title'])
			if cleaned_recording_title in cleaned_file_stem or cleaned_file_stem in cleaned_recording_title:
				return recording['id']

		# TODO: More advanced heuristics (e.g., artist matching)

		# If no good match is found, return the first result as a fallback
		return search_results['recording-list'][0]['id']

	def _clean_string(self, text: str) -> str:
		"""
		Removes special characters and converts to lowercase for better matching.
		"""
		return re.sub(r'[^a-zA-Z0-9]', '', text.lower())

	def _confirm_recording(self, recording_id: str) -> bool:
		"""
		Prompts the user to confirm if the automatically selected recording is correct.
		"""
		try:
			recording = musicbrainzngs.get_recording_by_id(recording_id, includes=['artists'])
			artist = recording['recording']['artist-credit'][0]['artist']['name']
			title = recording['recording']['title']
			confirmation = input(f"Found: {artist} - {title}. Is this correct? (y/n): ")
			return confirmation.lower() == 'y'
		except musicbrainzngs.MusicBrainzError as e:
			self._logger.error(f"MusicBrainzError: {e}")
			return False

	def _get_manual_mbid(self, file: Path) -> str or None:
		"""
		Prompts the user to enter the MusicBrainz ID manually or skip.
		"""
		while True:
			user_input = input(f"Could not find metadata for {file.name}. "
			                   "Enter MusicBrainz ID manually or 's' to skip: ")
			if user_input.lower() == 's':
				return None
			if self._is_valid_mbid(user_input):
				return user_input
			else:
				self._logger.error("Invalid MusicBrainz ID format.")

	def _is_valid_mbid(self, mbid: str) -> bool:
		"""
		Checks if the given string is a valid MusicBrainz ID format.
		"""
		pattern = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
		return bool(re.match(pattern, mbid))

	def _embed_metadata(self, file: Path, recording_id: str):
		"""
		Embeds as much metadata as possible from MusicBrainz into the FLAC file for Plexamp compatibility.
		"""
		try:
			recording = musicbrainzngs.get_recording_by_id(recording_id, includes=['artists', 'releases', 'tags'])

			# Extract artist information
			artist = recording['recording']['artist-credit'][0]['artist']['name']
			artist_id = recording['recording']['artist-credit'][0]['artist']['id']

			# Extract recording information
			title = recording['recording']['title']
			recording_length = int(recording['recording'].get('length', 0))  # in milliseconds

			# Get release information using the first release ID
			release_id = recording['recording']['release-list'][0]['id']
			release = musicbrainzngs.get_release_by_id(release_id, includes=['artist-credits', 'media', 'tags', 'release-groups'])['release']

			# Extract release information
			album = release['title']
			album_id = release['id']
			if 'artist-credit' in release:
				album_artist = release['artist-credit'][0]['artist']['name']
			else:
				album_artist = artist

			# Extract track and disc number from the correct medium
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

			release_date = release.get('date', None)
			genres = [tag['name'] for tag in release.get('tag-list', [])]

			# Use fallback values if necessary
			if not track_number:
				track_number = 1
			if not disc_number:
				disc_number = 1

			# Embed metadata using Mutagen
			audio = FLAC(file)
			audio['artist'] = artist
			audio['albumartist'] = album_artist
			audio['album'] = album
			audio['tracknumber'] = str(track_number)
			audio['discnumber'] = str(disc_number)
			audio['title'] = title
			if release_date:
				audio['date'] = release_date
			if genres:
				edited_genres = []

				for genre in genres:
					if genre == "Specify the genre of music":
						continue
					edited_genres.append(genre.replace(";", ", "))

				audio['genre'] = edited_genres
			if recording_length:
				audio['length'] = str(recording_length // 1000)  # Convert to seconds
			# ... add other metadata if available ...
			audio.save()
			self._place_file_correctly(file, genres[0], title, album, artist, track_number)

			self._logger.info(f"Embedded metadata into {file.name}")

		except musicbrainzngs.MusicBrainzError as e:
			self._logger.error(f"MusicBrainzError: {e}")
		except Exception as e:
			self._logger.error(f"Error embedding metadata: {e}")

	def _get_files(self) -> List[Path]:
		return self._file_helper.get_children_paths(DOWNLOAD_PATH, ".flac")

	def _place_file_correctly(self, file: Path, genre: str, track_title: str, track_album: str, track_artist: str, track_number: int) -> None:
		new_name: str = f"{track_number:02d} - {track_artist} - {track_title}.flac"
		new_path: Path = ORGANIZED_PATH.joinpath(genre).joinpath(track_album.replace("/", "-").replace(":", "_")).joinpath(new_name)

		# Make directories if necessary
		new_path.parent.mkdir(parents=True, exist_ok=True)

		file.rename(new_path)
		self._logger.info(f"Moved {file.name} to {new_path.parent.name}/{new_path.name}")
