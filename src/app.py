from pathlib import Path
from pprint import pprint
from typing import List

from py_common.cli_framework import CommandLineInterface
from py_common.logging import HoornLogger, HoornLogOutputInterface, DefaultHoornLogOutput, FileHoornLogOutput

from src.constants import DOWNLOAD_PATH, ORGANIZED_PATH
from src.downloading.music_download_interface import MusicDownloadInterface
from src.downloading.yt_dlp_music_downloader import YTDLPMusicDownloader
from src.metadata.metadata_api import MetadataAPI


def get_user_local_app_data_dir() -> Path:
	return Path.home() / "AppData" / "Local"

def get_user_log_directory() -> Path:
	return get_user_local_app_data_dir() / "Music Organization Tool/Logs"

def clean_exit(hlogger: HoornLogger):
	hlogger.debug("Clean Exit...")
	exit()

def clear_metadata_files(metadata_api: MetadataAPI):
	clear_options: List[str] = ["Genre", "Date"]
	choice: str = input("Choose a metadata option to clear (Genre/Date): ")

	if choice.lower() not in [option.lower() for option in clear_options]:
		logger.error(f"Invalid option '{choice.lower()}'. Choose from: {', '.join(clear_options)}")
		return clear_metadata_files(metadata_api)

	directory = Path(input("Enter the directory path to clear metadata: "))

	if choice.lower() == "genre":
		metadata_api.clear_genres(directory)
	elif choice.lower() == "date":
		metadata_api.clear_dates(directory)

def print_metadata_keys(metadata_api: MetadataAPI):
	audio_file = Path(input("Enter the path to the audio file: "))
	metadata_keys = metadata_api.get_metadata_keys(audio_file)
	print("Available metadata keys:")
	for key in metadata_keys:
		pprint(f"- {key}")

def populate_metadata_from_musicbrainz(metadata_api: MetadataAPI):
	metadata_api.populate_metadata_from_musicbrainz(Path(input("Enter the directory path to populate metadata: ")))

def organize_music_files(metadata_api: MetadataAPI):
	directory_path = input("Enter the directory path to organize music (leave empty for default): ")
	organized_path = input("Enter the directory path to save organized music (leave empty for default): ")

	if directory_path == "":
		directory_path = DOWNLOAD_PATH
	else: directory_path = Path(directory_path)
	if organized_path == "":
		organized_path = ORGANIZED_PATH
	else: organized_path = Path(organized_path)

	metadata_api.organize_music_files(directory_path, organized_path)

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
	metadata_api: MetadataAPI = MetadataAPI(logger)

	cli: CommandLineInterface = CommandLineInterface(logger)
	cli.add_command(["exit", "quit"], "Exit the program.", clean_exit, arguments=[logger])
	cli.add_command(["download"], "Download music files.", downloader.download_track)
	cli.add_command(["metadata", "md"], "Find metadata for a given song.", populate_metadata_from_musicbrainz, arguments=[metadata_api])
	cli.add_command(["clear"], "Clear metadata files.", clear_metadata_files, arguments=[metadata_api])
	cli.add_command(["db_keys"], "Print available metadata keys.", print_metadata_keys, arguments=[metadata_api])
	cli.add_command(["organize"], "Organize music files.", organize_music_files, arguments=[metadata_api])

	cli.start_listen_loop()
