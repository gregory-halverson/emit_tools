import numpy as np

from .constants import *
from .emit_xarray import emit_xarray

def emit_ortho_xarray(
        filepath: str, 
        qmask: np.ndarray = None, 
        unpacked_bmask: np.ndarray = None, 
        fill_value: int = FILL_VALUE,
        engine: str = ENGINE):
    """
    Load an EMIT NetCDF dataset and orthorectify it as an xarray.Dataset.

    Parameters:
    filepath: a filepath to an EMIT netCDF file
    qmask: a numpy array output from the quality_mask function used to mask pixels based on quality flags selected in that function. Any non-orthorectified array with the proper crosstrack and downtrack dimensions can also be used.
    unpacked_bmask: a numpy array from  the band_mask function that can be used to mask band-specific pixels that have been interpolated.

    Returns:
    out_xr: an xarray.Dataset constructed based on the parameters provided.

    """
    return emit_xarray(
        filepath=filepath,
        ortho=True,
        qmask=qmask,
        unpacked_bmask=unpacked_bmask,
        fill_value=fill_value,
        engine=engine
    )
