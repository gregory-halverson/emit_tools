import requests

from .constants import *

def concept_ID_from_DOI(DOI: str) -> str:
    """
    Find the concept ID for a given DOI.

    Parameters:
    DOI (str): The DOI to search for.

    Returns:
    str: The concept ID for the given DOI.
    """
    URL = f"{CMR_SEARCH_URL}collections.json?doi={DOI}"
    response = requests.get(URL)

    if response.status_code != 200:
        raise ValueError(f"Error: {response.status_code} - {response.text}")

    concept_ID = response.json()['feed']['entry'][0]['id']

    return concept_ID
