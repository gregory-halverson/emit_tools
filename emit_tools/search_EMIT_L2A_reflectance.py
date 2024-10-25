from typing import Union, Dict, Tuple, List
from datetime import date
import requests
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon
from shapely.geometry.polygon import orient
from dateutil import parser
import pandas as pd
import posixpath

from os.path import splitext

import rasters as rt
from rasters import RasterGeometry

from .constants import *
from .generate_CMR_daterange_string import generate_CMR_daterange_string

PAGE_NUM = 1
PAGE_SIZE = 2000

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

def extract_granules(granule_list_JSON: Dict) -> pd.DataFrame:
    """
    Extracts granule information from a JSON dictionary and returns it as a pandas DataFrame.

    Parameters:
    granule_list_JSON (Dict): A dictionary containing granule information. Each granule is expected to have
                              keys "title", "cloud_cover", "polygons", and "links".

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
        
        # Extract URLs to .nc and .png files, excluding .dmrpp files
        granule_urls = [x["href"] for x in granule_JSON["links"] if "https" in x["href"] and (".nc" in x["href"] or ".png" in x["href"]) and ".dmrpp" not in x["href"]]
        
        # Append the extracted information to the DataFrame
        df = pd.concat([df, pd.DataFrame({"URL": granule_urls, "cloud_percent": cloud_cover, "geometry": granule_poly})])
    
    # Return the final DataFrame containing all granule information
    return df

def iterate_CMR_pages(
        concept_ID: str, 
        temporal_search_string: str, 
        page_size: int, 
        granule_search_URL: str, 
        geojson: dict
    ) -> pd.DataFrame:
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
        response = requests.post(granule_search_URL, data=CMR_parameters, files=geojson)
        
        # Parse the JSON response to get the list of granules
        granule_list_JSON = response.json()['feed']['entry']
        
        # If no granules are found, exit the loop
        if len(granule_list_JSON) == 0:
            break
        
        # Extract granules into a DataFrame
        extracted_granules_df = extract_granules(granule_list_JSON)
        
        # Concatenate the extracted granules DataFrame with the main DataFrame
        df = pd.concat([df, extracted_granules_df])
        
        # Move to the next page
        page_num += 1
    
    # Return the compiled DataFrame
    return df

def search_EMIT_L2A_reflectance(
        start_date: Union[date, str], 
        end_date: Union[date, str], 
        target_area: Union[Polygon, RasterGeometry],
        concept_ID: str = EMIT_L2A_REFLECTANCE_CONCEPT_ID,
        granule_search_URL: str = CMR_GRANULE_SEARCH_URL,
        page_num = PAGE_NUM,
        page_size = PAGE_SIZE) -> gpd.GeoDataFrame:
    """
    Search for EMIT L2A reflectance data within a specified date range and target area.

    Parameters:
    start_date (Union[date, str]): The start date of the search range.
    end_date (Union[date, str]): The end date of the search range.
    target_area (Union[Polygon, RasterGeometry]): The geographical area to search within.
    concept_ID (str): The concept ID for the EMIT L2A reflectance product. Default is EMIT_L2A_REFLECTANCE_CONCEPT_ID.
    granule_search_URL (str): The URL for the granule search. Default is CMR_GRANULE_SEARCH_URL.
    page_num (int): The page number for pagination. Default is PAGE_NUM.
    page_size (int): The number of results per page. Default is PAGE_SIZE.

    Returns:
    gpd.GeoDataFrame: A GeoDataFrame containing the search results.
    """
    
    # Generate the temporal search string based on the start and end dates
    temporal_search_string = generate_CMR_daterange_string(start_date, end_date)

    # If the target area is a RasterGeometry, convert it to its boundary in lat/lon
    if isinstance(target_area, RasterGeometry):
        target_area = target_area.boundary_latlon

    # Ensure the target area polygon is oriented correctly
    target_area = orient(target_area, sign=1.0)
    
    # Create a GeoDataFrame from the target area polygon
    gdf = gpd.GeoDataFrame(geometry=[target_area])
    
    # Convert the GeoDataFrame to a GeoJSON format for the search
    geojson = {"shapefile": ("", gdf.to_json(), "application/geo+json")}

    # Perform the search by iterating through the CMR pages
    df = iterate_CMR_pages(
        concept_ID=concept_ID,
        temporal_search_string=temporal_search_string,
        page_size=page_size,
        granule_search_URL=granule_search_URL,
        geojson=geojson
    )

    # Drop granules with empty geometry, if any exist
    df = df[df['geometry'] != '']
    
    # Expand the DataFrame so each row contains a single URL
    df = df.explode('URL')
    
    # Extract and insert filename, product, date, level, datetime, orbit, scene, collection, and type information
    df.insert(0, 'filename', df.URL.str.split('/', n=-1).str.get(-1))
    df.insert(0, "product", df.filename.apply(lambda filename: "_".join(splitext(filename)[0].split("_")[1:3])))
    df.insert(0, "date_UTC", df.filename.apply(lambda filename: parser.parse(splitext(filename)[0].split("_")[4]).date()))
    df.insert(len(df.columns) - 1, "level", df.filename.apply(lambda filename: splitext(filename)[0].split("_")[1]))
    df.insert(len(df.columns) - 1, "datetime_UTC", df.filename.apply(lambda filename: parser.parse(splitext(filename)[0].split("_")[4])))
    df.insert(len(df.columns) - 1, "orbit", df.filename.apply(lambda filename: int(splitext(filename)[0].split("_")[5])))
    df.insert(len(df.columns) - 1, "scene", df.filename.apply(lambda filename: int(splitext(filename)[0].split("_")[6])))
    df.insert(len(df.columns) - 1, "collection", df.filename.apply(lambda filename: int(splitext(filename)[0].split("_")[3])))
    df.insert(len(df.columns) - 1, "type", df.filename.apply(lambda filename: classify_file_type(filename)))
    
    # Convert the DataFrame to a GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry='geometry')

    return gdf
    