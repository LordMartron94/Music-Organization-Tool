from pathlib import Path
from typing import List

from py_common.cli_framework import CommandLineInterface
from py_common.logging import HoornLogger, HoornLogOutputInterface, DefaultHoornLogOutput, FileHoornLogOutput

from src.metadata_finder import MetadataFinder
from src.music_download_interface import MusicDownloadInterface
from src.yt_dlp_music_downloader import YTDLPMusicDownloader


def get_user_local_app_data_dir() -> Path:
	return Path.home() / "AppData" / "Local"

def get_user_log_directory() -> Path:
	return get_user_local_app_data_dir() / "Music Organization Tool/Logs"

def clean_exit(hlogger: HoornLogger):
	hlogger.debug("Clean Exit...")
	exit()

if __name__ == "__main__":
	log_dir = get_user_log_directory()

	outputs: List[HoornLogOutputInterface] = [
		DefaultHoornLogOutput(),
		FileHoornLogOutput(log_dir, 5, True)
	]

	logger: HoornLogger = HoornLogger(
		outputs
	)

	downloader: MusicDownloadInterface = YTDLPMusicDownloader(logger)
	metadata_helper: MetadataFinder = MetadataFinder(logger)

	cli: CommandLineInterface = CommandLineInterface(logger)
	cli.add_command(["exit", "quit"], "Exit the program.", clean_exit, arguments=[logger])
	cli.add_command(["download"], "Download music files.", downloader.download_track)
	cli.add_command(["metadata", "md"], "Find metadata for a given song.", metadata_helper.find_and_embed_metadata)

	cli.start_listen_loop()
