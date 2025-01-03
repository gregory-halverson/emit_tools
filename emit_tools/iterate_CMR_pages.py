from typing import List, Optional
import pandas as pd
import requests

from .generate_CMR_parameters import generate_CMR_parameters
from .extract_granules_from_CMR_JSON import extract_granules_from_CMR_JSON

def iterate_CMR_pages(
        concept_ID: str,
        temporal_search_string: str,
        page_size: int,
        granule_search_URL: str,
        geojson: dict,
        allowed_extensions: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Iterates through pages of CMR (Common Metadata Repository) search results and compiles them into a DataFrame.

    Parameters:
    concept_ID (str): The concept ID for the CMR search.
    temporal_search_string (str): The temporal search string for filtering results.
    page_size (int): The number of results per page.
    granule_search_URL (str): The URL for the granule search.
    geojson (dict): The GeoJSON object for spatial filtering.

    Returns:
    pd.DataFrame: A DataFrame containing the compiled search results.
    """

    # Initialize an empty DataFrame with specified columns
    df = pd.DataFrame(columns=["URL", "cloud_percent", "geometry"])

    # Start with the first page
    page_num = 1

    while True:
        # Generate CMR parameters for the current page
        CMR_parameters = generate_CMR_parameters(
            concept_ID=concept_ID,
            temporal_search_string=temporal_search_string,
            page_num=page_num,
            page_size=page_size
        )

        # Send a POST request to the granule search URL with the CMR parameters and GeoJSON file
        response = requests.post(
            granule_search_URL, 
            data=CMR_parameters, 
            files=geojson
        )

        # Parse the JSON response to get the list of granules
        granule_list_JSON = response.json()['feed']['entry']

        # If no granules are found, exit the loop
        if len(granule_list_JSON) == 0:
            break

        # Extract granules into a DataFrame
        extracted_granules_df = extract_granules_from_CMR_JSON(
            granule_list_JSON=granule_list_JSON,
            allowed_extensions=allowed_extensions
        )

        # Concatenate the extracted granules DataFrame with the main DataFrame
        df = pd.concat([df, extracted_granules_df])

        # Move to the next page
        page_num += 1

    # Return the compiled DataFrame
    return df