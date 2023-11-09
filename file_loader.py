from persistence import Persistence
from activity import Activity
from load_file_data import load_file_data


def load_from_file(*, filename: str, elevation: int):
    """
    Load a FIT file
    """
    _load_from_file(filename=filename, elevation=elevation)


def _load_from_file(*, filename: str, elevation: int):
    """
    Load a FIT file.
    """

    # Load the file
    if not (activity_record := load_file_data(path=filename)):
        print(f"Couldn't find and load {filename}")

    # Add details
    activity_record.zwift_id = filename
    activity_record.s3_url = f"file://{filename}"

    # Derive the title from the filename
    activity_record.activity_name = _derive_title(filename=filename)

    # Capture the elevation
    activity_record.elevation = elevation

    # Save it
    db = Persistence()
    db.store(activity=activity_record)


def _derive_title(*, filename: str) -> str:

    # replace any underscores with spaces
    title: str = filename.replace("_", " ")

    # strip any extension
    ext = title.find(".")
    if ext != -1:
        title = title[0:ext]

    # Done
    return title
