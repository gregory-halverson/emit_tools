import posixpath

ENGINE = "netcdf4"
GLT_NODATA_VALUE = 0
FILL_VALUE = -9999
EMIT_L2A_REFLECTANCE_CONCEPT_ID = "C2408750690-LPCLOUD"
CMR_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
CMR_SEARCH_URL = "https://cmr.earthdata.nasa.gov/search/"
CMR_GRANULE_SEARCH_URL = posixpath.join(CMR_SEARCH_URL, "granules.json")
