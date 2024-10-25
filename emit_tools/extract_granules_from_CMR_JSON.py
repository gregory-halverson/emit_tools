from typing import Dict, List, Optional
import pandas as pd
from shapely.geometry import MultiPolygon, Polygon

def extract_granules_from_CMR_JSON(
        granule_list_JSON: Dict,
        allowed_extensions: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Extracts granule information from a JSON dictionary and returns it as a pandas DataFrame.

    Parameters:
    granule_list_JSON (Dict): A dictionary containing granule information. Each granule is expected to have
                              keys "title", "cloud_cover", "polygons", and "links".
    allowed_extensions (List[str], optional): List of allowed file extensions. Defaults to None.

    Returns:
    pd.DataFrame: A DataFrame with columns "URL", "cloud_percent", and "geometry" containing the extracted
                  granule information.
    """
    # Initialize an empty DataFrame with specified columns
    df = pd.DataFrame(columns=["URL", "cloud_percent", "geometry"])

    # Iterate over each granule in the input JSON dictionary
    for granule_JSON in granule_list_JSON:
        granule_urls = ""
        granule_poly = ""

        # Extract granule title and cloud cover percentage
        granule_name = granule_JSON["title"]
        cloud_cover = granule_JSON["cloud_cover"]

        # Check if the granule has bounding geometries
        if "polygons" in granule_JSON:
            polygons = granule_JSON["polygons"]
            multipolygons = []

            # Process each polygon to create a MultiPolygon object
            for poly in polygons:
                i = iter(poly[0].split(" "))
                ltln = list(map(" ".join, zip(i, i)))
                multipolygons.append(Polygon([[float(p.split(" ")[1]), float(p.split(" ")[0])] for p in ltln]))

            granule_poly = MultiPolygon(multipolygons)

        # Extract URLs to allowed files if allowed_extensions is provided
        if allowed_extensions:
            granule_urls = [x["href"] for x in granule_JSON["links"] if "https" in x["href"] and any(ext in x["href"] for ext in allowed_extensions)]
        else:
            granule_urls = [x["href"] for x in granule_JSON["links"] if "https" in x["href"]]

        # Append the extracted information to the DataFrame
        df = pd.concat([df, pd.DataFrame({"URL": granule_urls, "cloud_percent": cloud_cover, "geometry": granule_poly})])

    # Return the final DataFrame containing all granule information
    return df
