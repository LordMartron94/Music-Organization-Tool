import re

import yt_dlp

from src.constants import COOKIES_FILE


def download_video(url, output_template, sanitize_title=True):
	"""Downloads a video using yt-dlp and returns the sanitized file path.

	Args:
	  url: The URL of the video to download.
	  output_template: A string template for the output file name.
					   Can include yt-dlp formatting options (e.g., '%(title)s.%(ext)s').
	  sanitize_title: Whether to sanitize the title before downloading.

	Returns:
	  The sanitized file path of the downloaded video.
	"""

	ydl_opts = {
		'outtmpl': output_template,
		'format': 'bestaudio/best',  # Prioritize MP4
		'postprocessors': [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'flac',
			'preferredquality': '192',
		}],
		'noplaylist': True,
		"cookiefile": COOKIES_FILE
	}

	with yt_dlp.YoutubeDL(ydl_opts) as ydl:
		info_dict = ydl.extract_info(url, download=False)
		title = info_dict.get('title', 'audio')

		if sanitize_title:
			title = sanitize_filename(title)

		# Update the info_dict with the sanitized title and preferred extension
		info_dict['title'] = title
		info_dict['ext'] = 'flac'  # Set the expected extension after post-processing

		# Download the audio
		ydl.download([url])

		# Get the extracted audio file path
		file_path = ydl.prepare_filename(info_dict)

	return file_path


def sanitize_filename(filename):
	"""Sanitizes a filename by removing invalid characters."""

	# Remove invalid characters (replace with underscore)
	filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
	# Remove leading/trailing spaces
	filename = filename.strip()
	return filename

if __name__ == '__main__':
	path = download_video('https://www.youtube.com/watch?v=91dGIROGAa4&pp=ygURYmxhIGJsYSBibGEgdW5pcWU%3D', '%(title)s.%(ext)s' )
	print(f"Downloaded video saved as: {path}")
