import requests

from .constants import *

def concept_ID_from_short_name(short_name: str) -> str:
    """
    Find the concept ID for a given short name.

    Parameters:
    short_name (str): The short name to search for.

    Returns:
    str: The concept ID for the given short name.
    """
    URL = f"{CMR_SEARCH_URL}collections.json?short_name={short_name}"
    response = requests.get(URL)

    if response.status_code != 200:
        raise ValueError(f"Error: {response.status_code} - {response.text}")

    concept_ID = response.json()['feed']['entry'][0]['id']

    return concept_ID
