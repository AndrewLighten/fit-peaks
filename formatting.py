from calculation_data import AerobicDecoupling
from activity import Activity
from typing import List
from itertools import zip_longest


def format_aero_decoupling(*, aerobic_decoupling: AerobicDecoupling, width: int = 0) -> str:
    """
    Format a representation of the aerobic decoupling.
    
    Args:
        aerobic_decoupling: The aerobic decoupling data.
        width: The width to format to.
    
    Returns:
        The formatted representation.
    """

    if not aerobic_decoupling:
        return "".rjust(width) if width > 0 else ""

    coupling_text = format(aerobic_decoupling.coupling, ".1f") + "%"

    if width > 0:
        coupling_text = coupling_text.rjust(width)

    if aerobic_decoupling.coupling < 5:
        coupling_text = "\x1B[32m\x1B[1m" + coupling_text + "\x1B[0m"  # green
    elif aerobic_decoupling.coupling < 8:
        coupling_text = "\x1B[33m\x1B[1m" + coupling_text + "\x1B[0m"  # orange
    else:
        coupling_text = "\x1B[31m\x1B[1m" + coupling_text + "\x1B[0m"  # red

    return coupling_text


def format_aero_efficiency(*, aerobic_efficiency: float, width: int = 0) -> str:

    if not aerobic_efficiency:
        return "".rjust(width) if width > 0 else ""

    aerobic_efficiency_text = format(aerobic_efficiency, ".2f") + "%"

    if width > 0:
        aerobic_efficiency_text = aerobic_efficiency_text.rjust(width)

    if aerobic_efficiency > 2.2:
        aerobic_efficiency_text = "\x1B[32m\x1B[1m" + aerobic_efficiency_text + "\x1B[0m"  # green
    elif aerobic_efficiency > 2.0:
        aerobic_efficiency_text = "\x1B[33m\x1B[1m" + aerobic_efficiency_text + "\x1B[0m"  # orange
    else:
        aerobic_efficiency_text = "\x1B[31m\x1B[1m" + aerobic_efficiency_text + "\x1B[0m"  # red

    return aerobic_efficiency_text


def format_ctl(*, ctl: int, width: int = 0) -> str:
    ctl_text: str = str(ctl)
    if width > 0:
        ctl_text = ctl_text.rjust(width)
    return ctl_text


def format_atl(*, atl: int, width: int = 0) -> str:
    atl_text: str = str(atl)
    if width > 0:
        atl_text = atl_text.rjust(width)
    return atl_text


def format_tsb(*, tsb: int, width: int = 0) -> str:
    tsb_text: str = str(tsb)
    if width > 0:
        tsb_text = tsb_text.rjust(width)
    return tsb_text


def format_variability_index(*, activity: Activity, width: int = 0) -> str:
    """
    Format a representation of the variability index.
    
    Args:
        activity: The activity whose variability index should be formatted.
        width: The width to format to.
    
    Returns:
        The formatted representation.
    """

    if activity.variability_index is None or activity.distance < 10000:
        return "".rjust(width) if width else ""

    variability_index = format(activity.variability_index, ".0f") + "%"

    if width > 0:
        variability_index = variability_index.rjust(width)

    if activity.variability_index < 9:
        variability_index = "\x1B[32m\x1B[1m" + variability_index + "\x1B[0m"
    elif activity.variability_index < 13:
        variability_index = "\x1B[33m\x1B[1m" + variability_index + "\x1B[0m"
    else:
        variability_index = "\x1B[31m\x1B[1m" + variability_index + "\x1B[0m"

    return variability_index


class LeftRightPrinter:
    """
    This class provides support for printing two columns of text, side-by-side.
    """

    def __init__(self, left_width: int = 80):
        """
        Initialise the printer.
        
        Args:
            left_width: The width of the left-hand column. Defaults to 80.
        """
        self.left_width = left_width
        self.left: List[str] = []
        self.right: List[str] = []

    def add_left(self, text: str = ""):
        """
        Add text to the left-hand column
        
        Args:
            text: A line of text for the left-hand column. Defaults to "".
        """
        self.left.append(text)

    def add_right(self, text: str = ""):
        """
        Add text to the right-hand column
        
        Args:
            text: A line of text for the right-hand column. Defaults to "".
        """
        self.right.append(text)

    def print(self):
        """
        Print the text we've accumulated.
        """

        # Fetch an iterator that gives us both lists of text: left and right
        lines = zip_longest(self.left, self.right)

        # Visit each line
        for line in lines:

            # Print the left column
            if line[0]:
                print(line[0], end="")
                print(" " * (self.left_width - self._get_text_width(line[0])), end="")
            else:
                print(" ".ljust(self.left_width), end="")

            # Print the right column
            print((line[1] if line[1] else ""))

    def _get_text_width(self, text: str) -> int:
        """
        Get the width of a text string, but specifically ignore any
        ANSI colour sequences.
        
        Args:
            text: The string we want the displayed glyph length of.
        
        Returns:
            The string's displayed length.
        """

        # Initialise
        in_ansi = False
        width = 0

        # Visit each character
        for ch in text:

            # Entering or leaving an ANSI sequence?
            if ch == "\x1B":
                in_ansi = True
            elif ch == "m" and in_ansi:
                in_ansi = False

            # if not in an ANSI sequence, count this character
            elif not in_ansi:
                width += 1

        # Done
        return width
