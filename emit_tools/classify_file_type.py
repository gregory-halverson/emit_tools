from os.path import splitext


def classify_file_type(filename: str) -> str:
    """
    Classifies the type of a file based on its extension.

    Args:
        filename (str): The name of the file to classify.

    Returns:
        str: The type of the file. Possible values are:
             - "data" for NetCDF files (".nc")
             - "browse" for PNG image files (".png")
             - "unknown" for any other file types
    """
    extension = splitext(filename)[1]

    if extension == ".nc":
        return "data"
    elif extension == ".png":
        return "browse"
    else:
        return "unknown"
