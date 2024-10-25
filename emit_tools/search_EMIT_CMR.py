from emit_tools.classify_file_type import classify_file_type
from emit_tools.constants import CMR_GRANULE_SEARCH_URL, PAGE_NUM
from emit_tools.generate_CMR_daterange_string import generate_CMR_daterange_string
from emit_tools.iterate_CMR_pages import iterate_CMR_pages
from emit_tools.constants import PAGE_SIZE


from dateutil import parser
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient


from datetime import date
from os.path import splitext


def search_EMIT_CMR(
        start_date: Union[date, str],
        end_date: Union[date, str],
        target_area: Union[Polygon, RasterGeometry],
        concept_ID: str,
        granule_search_URL: str = CMR_GRANULE_SEARCH_URL,
        page_num = PAGE_NUM,
        page_size = PAGE_SIZE) -> gpd.GeoDataFrame:
    """
    Search for EMIT data within a specified date range and target area.

    Parameters:
    start_date (Union[date, str]): The start date of the search range.
    end_date (Union[date, str]): The end date of the search range.
    target_area (Union[Polygon, RasterGeometry]): The geographical area to search within.
    concept_ID (str): The concept ID for the EMIT product.
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