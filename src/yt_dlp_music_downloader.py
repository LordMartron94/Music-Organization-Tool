import os.path

import yt_dlp
from py_common.logging import HoornLogger

from src.constants import DOWNLOAD_PATH
from src.music_download_interface import MusicDownloadInterface


class YTDLPMusicDownloader(MusicDownloadInterface):
	def __init__(self, logger: HoornLogger):
		super().__init__(is_child=True)
		self._logger = logger
		self._logger.debug("YTDLPMusicDownloader initialized")

	def download_track(self) -> None:
		url: str = input("Enter the music URL: ")

		ydl_opts = {
			'format': 'bestaudio/best',  # Download the best available audio
			'postprocessors': [{
				'key': 'FFmpegExtractAudio',
				'preferredcodec': 'flac',
				'preferredquality': '192',
			}],
			'outtmpl': os.path.join(DOWNLOAD_PATH, '%(title)s.%(ext)s'),
			'noplaylist': True
		}

		with yt_dlp.YoutubeDL(ydl_opts) as ydl:
			ydl.download([url])
