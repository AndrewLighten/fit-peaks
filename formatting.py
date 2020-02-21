from calculation_data import AerobicDecoupling
from activity import Activity


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
        coupling_text = "\033[32m\033[1m" + coupling_text + "\033[0m"
    elif aerobic_decoupling.coupling < 8:
        coupling_text = "\033[33m\033[1m" + coupling_text + "\033[0m"
    else:
        coupling_text = "\033[31m\033[1m" + coupling_text + "\033[0m"

    return coupling_text


def format_variability_index(*, activity: Activity, width: int = 0) -> str:

    if activity.variability_index is None or activity.distance < 10000:
        return "".rjust(width) if width else ""

    variability_index = format(activity.variability_index, ".0f") + "%"

    if width > 0:
        variability_index = variability_index.rjust(width)

    if activity.variability_index < 9:
        variability_index = "\033[32m\033[1m" + variability_index + "\033[0m"
    elif activity.variability_index < 13:
        variability_index = "\033[33m\033[1m" + variability_index + "\033[0m"
    else:
        variability_index = "\033[31m\033[1m" + variability_index + "\033[0m"

    return variability_index
