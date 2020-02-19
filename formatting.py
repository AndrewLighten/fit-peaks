from calculation_data import AerobicDecoupling

def format_aero_decoupling(*, aerobic_decoupling: AerobicDecoupling, width: int=0) -> str:
    """
    Format a representation of the aerobic decoupling.
    
    Args:
        aerobic_decoupling: The aerobic decoupling data.
        width: The width to format to.
    
    Returns:
        The formatted representation.
    """

    if not aerobic_decoupling:
        return "".rjust(width) if width>0 else ""

    coupling_text = format(aerobic_decoupling.coupling, ".1f") + "%"

    if width>0:
        coupling_text = coupling_text.rjust(width)

    if aerobic_decoupling.coupling < 5:
        coupling_text = "\033[32m\033[1m" + coupling_text + "\033[0m"
    elif aerobic_decoupling.coupling < 8:
        coupling_text = "\033[33m\033[1m" + coupling_text + "\033[0m"
    else:
        coupling_text = "\033[31m\033[1m" + coupling_text + "\033[0m"

    return coupling_text
