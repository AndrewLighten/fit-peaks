import os

import fitparse.utils
from persistence import Persistence
from peaks import Peaks
from file_peaks import get_file_peaks


SOURCE_DIR = "/Users/andrew/Documents/Zwift/Activities"


def load_from_zwift():
    """
    Load the latest data from Zwift.
    """

    # Initialise.
    db = Persistence()
    loaded = 0

    # Visit each file in the Zwift activity directory.
    for filename in os.listdir(SOURCE_DIR):

        # Ignore the in progress file.
        if filename == "inProgressActivity.fit":
            continue

        # See if we've already got this file.
        if db.load(filename=filename):
            continue

        # No, so load it.
        print(f"Loading {filename}...")

        # Some files are busted -- they contain data that the fitparse library
        # can't handle.
        try:

            # Load the file, then persist our peak data.
            new_peaks = get_file_peaks(path=SOURCE_DIR + "/" + filename)
            db.store(filename=filename, peaks=new_peaks)
            loaded += 1

        # This is a busted file.
        except fitparse.utils.FitParseError:
            print(f"> Failed to load file")

    # Done.
    print(f"Loaded {loaded} file(s)")
