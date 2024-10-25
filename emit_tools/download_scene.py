# download_scene_module.py

import pandas as pd
from os.path import join

from .download_file import download_file

def download_scene(
        CMR_results_df: pd.DataFrame, 
        directory: str,
        orbit: int,
        scene: int) -> list:
    """
    Downloads specific scene files from a given DataFrame of CMR results.

    Parameters:
    CMR_results_df (pd.DataFrame): DataFrame containing CMR results with columns 'orbit', 'scene', 'URL', and 'filename'.
    directory (str): Directory where the downloaded files will be saved.
    orbit (int): Orbit number to filter the DataFrame.
    scene (int): Scene number to filter the DataFrame.

    Returns:
    list: List of filenames of the downloaded files.
    """
    # Create a copy of the DataFrame to avoid modifying the original data
    df = CMR_results_df.copy()
    
    # Filter the DataFrame to include only rows with the specified orbit number
    df = df[df.orbit == orbit]
    
    # Further filter the DataFrame to include only rows with the specified scene number
    df = df[df.scene == scene]

    # Initialize an empty list to store the filenames of downloaded files
    downloaded_files = []

    # Iterate over each row in the filtered DataFrame
    for granule_row in df.iterrows():
        # Extract the URL from the current row
        URL = granule_row[1].URL
        print(URL)
        
        # Extract the base filename from the current row
        filename_base = granule_row[1].filename
        
        # Create the full path for the file to be saved
        filename = join(directory, filename_base)
        
        # Download the file from the URL and save it to the specified directory
        download_file(URL, filename)
        
        # Append the downloaded filename to the list
        downloaded_files.append(filename)
    
    # Return the list of downloaded filenames
    return downloaded_files
