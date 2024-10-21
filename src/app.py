from pathlib import Path
from typing import List

from py_common.logging import HoornLogger, HoornLogOutputInterface, DefaultHoornLogOutput, FileHoornLogOutput

def get_user_local_app_data_dir() -> Path:
	return Path.home() / "AppData" / "Local"

def get_user_log_directory() -> Path:
	return get_user_local_app_data_dir() / "Music Organization Tool/Logs"


if __name__ == "__main__":
	log_dir = get_user_log_directory()

	outputs: List[HoornLogOutputInterface] = [
		DefaultHoornLogOutput(),
		FileHoornLogOutput(log_dir, 5, True)
	]

	logger: HoornLogger = HoornLogger(
		outputs
	)
