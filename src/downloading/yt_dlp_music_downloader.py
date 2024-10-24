import os.path
import re
from pathlib import Path
from pprint import pprint
from typing import List

import yt_dlp
from py_common.logging import HoornLogger

from src.constants import DOWNLOAD_PATH, DOWNLOAD_CHECKER_FILE, COOKIES_FILE, DOWNLOAD_CSV_FILE
from src.downloading.download_model import DownloadModel
from src.downloading.music_download_interface import MusicDownloadInterface


class YTDLPMusicDownloader(MusicDownloadInterface):
	def __init__(self, logger: HoornLogger):
		super().__init__(is_child=True)
		self._logger = logger
		self._logger.debug("YTDLPMusicDownloader initialized")

	def download_tracks(self) -> List[DownloadModel]:
		choice = self._get_choice()
		if choice.lower() =='single':
			return [self._download_single_track()]
		elif choice.lower() =='multiple':
			return self._download_multiple_tracks()
		elif choice.lower() == 'csv':
			return self._download_csv_tracks()

	def _download_single_track(self) -> DownloadModel:
		url = input("Enter the music URL: ")
		path: Path = self._download_urls([url])[0]
		return DownloadModel(url=url, path=path)

	def _download_multiple_tracks(self) -> List[DownloadModel]:
		file_path = input("Enter the file path containing the music URLs (one per line, leave empty for default): ")

		if file_path == "":
			file_path = DOWNLOAD_CHECKER_FILE
		else: file_path = Path(file_path)

		# validate file path
		if not os.path.isfile(file_path):
			self._logger.error(f"File not found: {file_path}")
			return []

		with open(file_path, 'r') as file:
			urls = [line.strip() for line in file.readlines()]
			paths: List[Path] = self._download_urls(urls)

			download_models = []
			for i in range(len(urls)):
				download_models.append(DownloadModel(url=urls[i], path=paths[i]))

			return download_models

	def _download_csv_tracks(self) -> List[DownloadModel]:
		file_path = input("Enter the file path containing the music URLs (csv, leave empty for default): ")

		if file_path == "":
			file_path = DOWNLOAD_CSV_FILE
		else: file_path = Path(file_path)

		# validate file path
		if not os.path.isfile(file_path):
			self._logger.error(f"File not found: {file_path}")
			return []

		with open(file_path, 'r') as file:
			data = file.readlines()[1:] # Skip the header line
			urls = []
			release_ids = []
			recording_ids = []
			genres = []
			subgenres = []

			for line in data:
				parts = line.strip().split(',')
				urls.append(parts[0])
				release_ids.append(parts[1])
				recording_ids.append(parts[2])
				genres.append(parts[3])
				subgenres.append(parts[4])

			paths: List[Path] = self._download_urls(urls)

			recording_models: List[DownloadModel] = []
			for i in range(len(urls)):
				recording_models.append(DownloadModel(
                    url=urls[i],
					path=paths[i],
                    release_id=release_ids[i],
                    recording_id=recording_ids[i],
                    genre=genres[i],
                    subgenre=subgenres[i]
                ))

			return recording_models

	def _download_urls(self, urls: List[str]) -> List[Path]:
		ydl_opts = {
			'format': 'bestaudio/best',
			'postprocessors': [{
				'key': 'FFmpegExtractAudio',
				'preferredcodec': 'flac',
				'preferredquality': '192',
			}],
			'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s'),
			'noplaylist': True,
			"cookiefile": COOKIES_FILE
		}

		downloaded_files: List[Path] = []

		with yt_dlp.YoutubeDL(ydl_opts) as ydl:
			for url in urls:
				info_dict = ydl.extract_info(url, download=False)
				title = info_dict.get('title', 'audio')
				title = self._clean_filename(title)

				# Update the info_dict with the sanitized title and preferred extension
				info_dict['title'] = title
				info_dict['ext'] = 'flac'  # Set the expected extension after post-processing
				ydl_opts['outtmpl']['default'] = os.path.join(DOWNLOAD_PATH, f'{title}.%(ext)s')  # Update the output template with the sanitized title

				# Download the audio
				ydl.download([url])

				# Get the extracted audio file path
				file_path = ydl.prepare_filename(info_dict)
				downloaded_files.append(Path(file_path))

		return downloaded_files

	def _get_choice(self) -> str:
		choice = input("Choose a download option (single/multiple/csv): ")
		if choice.lower() not in ['single','multiple', 'csv']:
			self._logger.error(f"Invalid option '{choice}'. Choose from: single, multiple")
			return self._get_choice()

		return choice

	def _clean_filename(self, filename: str, replacement_char='_') -> str:
		"""
		Cleans a filename by removing unsupported characters and replacing them
		with a specified character (default: '_').

		Args:
		  filename: The filename to clean.
		  replacement_char: The character to replace unsupported characters with.

		Returns:
		  The cleaned filename.
		"""
		# Define a regular expression to match invalid characters
		invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'

		# Replace invalid characters with the replacement character
		cleaned_filename = re.sub(invalid_chars, replacement_char, filename)

		# Remove leading and trailing spaces and dots
		cleaned_filename = cleaned_filename.strip(' .')

		# Ensure the filename is not empty
		if not cleaned_filename:
			cleaned_filename = replacement_char

		return cleaned_filename
