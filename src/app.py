from pathlib import Path
from pprint import pprint
from typing import List

from py_common.cli_framework import CommandLineInterface
from py_common.logging import HoornLogger, HoornLogOutputInterface, DefaultHoornLogOutput, FileHoornLogOutput, LogType

from src.constants import DOWNLOAD_PATH, ORGANIZED_PATH
from src.downloading.download_model import DownloadModel
from src.downloading.music_download_interface import MusicDownloadInterface
from src.downloading.yt_dlp_music_downloader import YTDLPMusicDownloader
from src.genre_detection.genre_algorithm import GenreAlgorithm
from src.metadata.helpers.track_model import TrackModel
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
	directory_path = input("Enter the directory path to populate metadata (leave empty for default): ")

	if directory_path == "":
		directory_path = DOWNLOAD_PATH
	else: directory_path = Path(directory_path)

	metadata_api.populate_metadata_from_musicbrainz(directory_path)

def populate_metadata_from_musicbrainz_album(metadata_api: MetadataAPI):
	directory_path = input("Enter the directory path to populate metadata (leave empty for default): ")
	album_id = input("Enter the MusicBrainz album ID: ")

	if directory_path == "":
		directory_path = DOWNLOAD_PATH
	else: directory_path = Path(directory_path)

	metadata_api.populate_metadata_from_musicbrainz_album(directory_path, album_id)

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

def recheck_missing_metadata(metadata_api: MetadataAPI):
	organized_path = input("Enter the directory path to save organized music (leave empty for default): ")

	if organized_path == "":
		organized_path = ORGANIZED_PATH
	else: organized_path = Path(organized_path)

	metadata_api.recheck_missing_metadata(organized_path)

def rescan_entire_library(metadata_api: MetadataAPI):
	organized_path = input("Enter the directory path to save organized music (leave empty for default): ")

	if organized_path == "":
		organized_path = ORGANIZED_PATH
	else: organized_path = Path(organized_path)

	metadata_api.rescan_entire_library(organized_path)

def download_and_assign_metadata(downloader: MusicDownloadInterface, metadata_api: MetadataAPI):
	download_files: List[DownloadModel] = downloader.download_tracks()

	for download_model in download_files:
		metadata_api.populate_metadata_from_musicbrainz_for_file(download_model)

def make_description_compatible_for_library(metadata_api: MetadataAPI):
	organized_path = input("Enter the directory path to save organized music (leave empty for default): ")

	if organized_path == "":
		organized_path = ORGANIZED_PATH
	else: organized_path = Path(organized_path)

	metadata_api.make_description_compatible_for_library(organized_path)

def print_track_ids_from_album(metadata_api: MetadataAPI):
	track_models: List[TrackModel] = metadata_api.get_track_ids_from_album()
	print("Track IDs:")
	for track_model in track_models:
		print(f"- {track_model.track_number} - {track_model.mbid} - {track_model.title}")

def get_genre_data(genre_algorithm: GenreAlgorithm):
	track_id: str = input("Enter the MusicBrainz track ID: ")
	album_id: str = input("Enter the MusicBrainz album ID: ")

	genre_algorithm.get_genre_data(track_id, album_id)

if __name__ == "__main__":
	log_dir = get_user_log_directory()

	outputs: List[HoornLogOutputInterface] = [
		DefaultHoornLogOutput(),
		FileHoornLogOutput(log_dir, 5, True)
	]

	logger: HoornLogger = HoornLogger(
		outputs,
		min_level=LogType.DEBUG,
	)

	downloader: MusicDownloadInterface = YTDLPMusicDownloader(logger)
	genre_algorithm: GenreAlgorithm = GenreAlgorithm(logger)
	metadata_api: MetadataAPI = MetadataAPI(logger, genre_algorithm)

	cli: CommandLineInterface = CommandLineInterface(logger)
	cli.add_command(["download"], "Download music files.", downloader.download_tracks)
	cli.add_command(["download-and-md"], "Combines downloading and setting metadata.", download_and_assign_metadata, arguments=[downloader, metadata_api])
	cli.add_command(["metadata", "md"], "Find metadata for the library.", populate_metadata_from_musicbrainz, arguments=[metadata_api])
	cli.add_command(["metadata-album", "md-a"], "Finds metadata using album... Faster, less input required.", populate_metadata_from_musicbrainz_album, arguments=[metadata_api])
	cli.add_command(["clear"], "Clear metadata files.", clear_metadata_files, arguments=[metadata_api])
	cli.add_command(["db_keys"], "Print available metadata keys.", print_metadata_keys, arguments=[metadata_api])
	cli.add_command(["organize"], "Organize music files.", organize_music_files, arguments=[metadata_api])
	cli.add_command(["recheck"], "Recheck missing metadata.", recheck_missing_metadata, arguments=[metadata_api])
	cli.add_command(["rescan"], "Rescans the entire library recursively.", rescan_entire_library, arguments=[metadata_api])
	cli.add_command(["compatible"], "Make description compatible for the library.", make_description_compatible_for_library, arguments=[metadata_api])
	cli.add_command(["get-tracks"], "Prints the IDs for all tracks in an Album.", print_track_ids_from_album, arguments=[metadata_api])
	cli.add_command(["add-album-to-downloads"], "Adds an album to the downloads.csv file.", metadata_api.add_album_to_downloads)
	cli.add_command(["get-genre"], "Retrieves genre information for a track.", get_genre_data, arguments=[genre_algorithm])

	cli.start_listen_loop()
