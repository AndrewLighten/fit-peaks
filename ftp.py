from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path
import json

FTP_FILE = str(Path.home()) + "/.ftp.json"


@dataclass
class FTP:
    """
    This class represents an FTP we've loaded from the FTP file.
    """

    start_date: datetime
    ftp: int


def get_ftp(when: datetime) -> Optional[int]:
    """
    Get the FTP value that is in effect for a particular date.
    
    Args:
        when: The date we want an FTP value for.
    
    Returns:
        Optional[int]: The FTP in effect for that date, if any.
    """

    # Fetch the FTP list
    if not (ftp_list := _get_all_ftp_values()):
        return None
    when = when.replace(tzinfo=None)

    # Find the FTP entry with the latest date equal to or before
    # the provided date
    selected_ftp = None
    for ftp in ftp_list:
        if ftp.start_date.date() < when.date():
            selected_ftp = ftp.ftp
    
    # Done
    return selected_ftp


def _get_all_ftp_values() -> Optional[List[FTP]]:
    """
    Fetch the list of all FTP values.
    
    Returns:
        Optional[List[FTP]]: The loaded FTP data.
    """

    # Be ready for problems
    try:

        # Load the JSON array of FTP data
        with open(FTP_FILE) as json_file:
            ftp_values = json.load(json_file)
            return [FTP(datetime.strptime(raw_ftp["date"], "%d-%b-%Y"), raw_ftp["ftp"]) for raw_ftp in ftp_values]

    # No FTP data available
    except FileNotFoundError:
        return None
