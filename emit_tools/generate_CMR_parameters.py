from typing import Dict

from .constants import *

def generate_CMR_parameters(
        concept_ID: str,
        temporal_search_string: str,
        page_num = PAGE_NUM,
        page_size = PAGE_SIZE) -> Dict:
    """
    Generate parameters for a CMR (Common Metadata Repository) search.

    Args:
        concept_ID (str): The concept ID of the collection to search.
        temporal_search_string (str): The temporal search string in the format required by CMR.
        page_num (int, optional): The page number for paginated results. Defaults to PAGE_NUM.
        page_size (int, optional): The number of results per page. Defaults to PAGE_SIZE.

    Returns:
        Dict: A dictionary containing the parameters for the CMR search.
    """
    CMR_parameters = {
        "collection_concept_id": concept_ID,
        "page_size": page_size,
        "page_num": page_num,
        "temporal": temporal_search_string,
        "simplify-shapefile": 'true'  # this is needed to bypass 5000 coordinates limit of CMR
    }

    return CMR_parameters
