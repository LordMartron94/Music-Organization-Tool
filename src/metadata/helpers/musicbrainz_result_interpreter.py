from py_common.logging import HoornLogger


class MusicBrainzResultInterpreter:
	"""Utility class to interpret MusicBrainz search results."""
	def __init__(self, logger: HoornLogger):
		self._logger = logger

	def choose_best_result(self, search_results, file_stem) -> str or None:
		"""
		Lets the user choose the best matching MusicBrainz recording ID from the search results.
		"""
		if not search_results['recording-list']:
			return None

		filtered_list = search_results['recording-list'][:10]

		self._logger.info("Found multiple MusicBrainz recordings for '{}'. Choose the correct one.".format(file_stem))
		number = -1
		for recording in filtered_list:
			number += 1
			self._logger.info("{}. Recording ID: {}, Title: {}, Artist: {}".format(number, recording['id'], recording['title'], recording['artist-credit'][0]['name']))

			# Check if contains release list
			if "release-list" in recording.keys():
				self._logger.info("Possible releases: {}".format(", ".join([release['title'] for release in recording['release-list'][:5]])))
			else: self._logger.info("Possible releases: None")


		choice = input("Enter the number of the recording you want to use (or -1 to skip, or -2 to manually type an ID, empty for the first): ")
		if choice == "":
			return filtered_list[0]['id']
		if -1 <= int(choice) < len(search_results['recording-list']):
			return search_results['recording-list'][int(choice)]['id']
		if int(choice) == -2:
			return input("Enter the MusicBrainz recording ID manually: ")

		return None
