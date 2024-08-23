from typing import Union
from datetime import date
import requests
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon
from shapely.geometry.polygon import orient
from dateutil import parser
import pandas as pd

from .generate_CMR_daterange_string import generate_CMR_daterange_string

def search_EMIT_L2A_reflectance(start_date: Union[date, str], end_date: Union[date, str], polygon: Polygon) -> gpd.GeoDataFrame:
    page_num = 1
    page_size = 2000 # CMR page size limit
    concept_ID = "C2408750690-LPCLOUD"
    cmrurl='https://cmr.earthdata.nasa.gov/search/' 

    temporal_str = generate_CMR_daterange_string(start_date, end_date)

    polygon = orient(polygon, sign=1.0)
    gdf = gpd.GeoDataFrame(geometry=[polygon])
    geojson = {"shapefile": ("", gdf.to_json(), "application/geo+json")}

    granule_arr = []

    while True:
        
        # defining parameters
        cmr_param = {
            "collection_concept_id": concept_ID, 
            "page_size": page_size,
            "page_num": page_num,
            "temporal": temporal_str,
            "simplify-shapefile": 'true' # this is needed to bypass 5000 coordinates limit of CMR
        }

        granulesearch = cmrurl + 'granules.json'
        response = requests.post(granulesearch, data=cmr_param, files=geojson)
        print(response)
        print(response.json())
        granules = response.json()['feed']['entry']
        
        if granules:
            for g in granules:
                granule_urls = ''
                granule_poly = ''
                        
                # read granule title and cloud cover
                granule_name = g['title']
                cloud_cover = g['cloud_cover']
        
                # reading bounding geometries
                if 'polygons' in g:
                    polygons= g['polygons']
                    multipolygons = []
                    for poly in polygons:
                        i=iter(poly[0].split (" "))
                        ltln = list(map(" ".join,zip(i,i)))
                        multipolygons.append(Polygon([[float(p.split(" ")[1]), float(p.split(" ")[0])] for p in ltln]))
                    granule_poly = MultiPolygon(multipolygons)
                
                # Get https URLs to .nc files and exclude .dmrpp files
                granule_urls = [x['href'] for x in g['links'] if 'https' in x['href'] and '.nc' in x['href'] and '.dmrpp' not in x['href']]
                # Add to list
                granule_arr.append([granule_urls, cloud_cover, granule_poly])
                            
            page_num += 1
        else: 
            break
    
    # creating a pandas dataframe
    df = pd.DataFrame(granule_arr, columns=["URL", "cloud_percent", "geometry"])
    # Drop granules with empty geometry - if any exist
    df = df[df['geometry'] != '']
    # Expand so each row contains a single url 
    df = df.explode('URL')
    # Name each asset based on filename
    df.insert(0,'filename', df.URL.str.split('/',n=-1).str.get(-1))
    df.insert(0, "product", df.filename.apply(lambda filename: "_".join(filename.split("_")[1:3])))
    df.insert(0, "date", df.filename.apply(lambda filename: parser.parse(filename.split("_")[3]).date()))
    # convert table to GeoDataFrame
    gdf = gpd.GeoDataFrame(df, geometry='geometry')

    return df
    