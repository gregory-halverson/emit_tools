from .constants import *

def CMR_collection_search_short_name_URL(short_name: str) -> str:
    return posixpath.join(CMR_SEARCH_URL, f"collections.json?short_name={short_name}")
