from typing import Union, Tuple, Optional
from datetime import date

import geopandas as gpd
from shapely.geometry import Polygon
import posixpath

from rasters import RasterGeometry

from .constants import *
from .search_EMIT_CMR import search_EMIT_CMR

def search_EMIT_L2B_carbon(
        start_date: Union[date, str], 
        end_date: Union[date, str], 
        target_area: Union[Polygon, RasterGeometry],
        concept_ID: str = EMIT_L2B_CARBON_CONCEPT_ID,
        granule_search_URL: str = CMR_GRANULE_SEARCH_URL,
        page_num = PAGE_NUM,
        page_size = PAGE_SIZE) -> gpd.GeoDataFrame:
    """
    Search for EMIT L2B carbon dioxide data within a specified date range and target area.

    Parameters:
    start_date (Union[date, str]): The start date of the search range.
    end_date (Union[date, str]): The end date of the search range.
    target_area (Union[Polygon, RasterGeometry]): The geographical area to search within.
    granule_search_URL (str): The URL for the granule search. Default is CMR_GRANULE_SEARCH_URL.
    page_num (int): The page number for pagination. Default is PAGE_NUM.
    page_size (int): The number of results per page. Default is PAGE_SIZE.

    Returns:
    gpd.GeoDataFrame: A GeoDataFrame containing the search results.
    """
    return search_EMIT_CMR(
        start_date=start_date,
        end_date=end_date,
        target_area=target_area,
        concept_ID=concept_ID,
        granule_search_URL=granule_search_URL,
        page_num=page_num,
        page_size=page_size,
        allowed_extensions=[".nc", ".png"]
    )
    