from .constants import *

def CMR_collection_search_DOI_URL(DOI: str) -> str:
    return posixpath.join(CMR_SEARCH_URL, f"collections.json?doi={DOI}")
