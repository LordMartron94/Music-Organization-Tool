import os.path
from pathlib import Path
from typing import List

import yt_dlp
from py_common.logging import HoornLogger

from src.constants import DOWNLOAD_PATH, DOWNLOAD_CHECKER_FILE, COOKIES_FILE
from src.downloading.music_download_interface import MusicDownloadInterface


class YTDLPMusicDownloader(MusicDownloadInterface):
	def __init__(self, logger: HoornLogger):
		super().__init__(is_child=True)
		self._logger = logger
		self._logger.debug("YTDLPMusicDownloader initialized")

	def download_track(self) -> None:
		choice = self._get_choice()
		if choice.lower() =='single':
			self._download_single_track()
		elif choice.lower() =='multiple':
			self._download_multiple_tracks()

	def _download_single_track(self) -> None:
		url = input("Enter the music URL: ")
		self._download_url([url])

	def _download_multiple_tracks(self) -> None:
		file_path = input("Enter the file path containing the music URLs (one per line, leave empty for default): ")

		if file_path == "":
			file_path = DOWNLOAD_CHECKER_FILE
		else: file_path = Path(file_path)

		# validate file path
		if not os.path.isfile(file_path):
			self._logger.error(f"File not found: {file_path}")
			return

		with open(file_path, 'r') as file:
			urls = [line.strip() for line in file.readlines()]
			self._download_url(urls)

	def _download_url(self, urls: List[str]) -> None:
		ydl_opts = {
			'format': 'bestaudio/best',  # Download the best available audio
			'postprocessors': [{
				'key': 'FFmpegExtractAudio',
				'preferredcodec': 'flac',
				'preferredquality': '192',
			}],
			'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s'),
			'noplaylist': True,
			"cookiefile": COOKIES_FILE
		}

		with yt_dlp.YoutubeDL(ydl_opts) as ydl:
			ydl.download(urls)

	def _get_choice(self) -> str:
		choice = input("Choose a download option (single/multiple): ")
		if choice.lower() not in ['single','multiple']:
			self._logger.error(f"Invalid option '{choice}'. Choose from: single, multiple")
			return self._get_choice()

		return choice