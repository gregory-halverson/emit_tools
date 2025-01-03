from typing import Dict, Optional

from .constants import *

def generate_CMR_parameters(
        concept_ID: str,
        temporal_search_string: Optional[str] = None,
        readable_granule_name: Optional[str] = None,
        page_num: int = PAGE_NUM,
        page_size: int = PAGE_SIZE) -> Dict:
    """
    Generate parameters for a CMR (Common Metadata Repository) search.

    Args:
        concept_ID (str): The concept ID of the collection to search.
        temporal_search_string (Optional[str], optional): The temporal search string in the format required by CMR.
        readable_granule_name (Optional[str], optional): The filename pattern for granule search.
        page_num (int, optional): The page number for paginated results. Defaults to PAGE_NUM.
        page_size (int, optional): The number of results per page. Defaults to PAGE_SIZE.

    Returns:
        Dict: A dictionary containing the parameters for the CMR search.
    """
    CMR_parameters = {
        "collection_concept_id": concept_ID,
        "page_size": page_size,
        "page_num": page_num,
        "simplify-shapefile": 'true'  # This bypasses the 5000 coordinates limit of CMR.
    }
    
    # Add temporal parameter if provided
    if temporal_search_string:
        CMR_parameters["temporal"] = temporal_search_string

    # Add readable granule name filter if provided
    if readable_granule_name:
        CMR_parameters["options[readable_granule_name][pattern]"] = 'true'
        CMR_parameters["readable_granule_name"] = readable_granule_name

    return CMR_parameters
