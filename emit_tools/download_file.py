import os
from os import makedirs
from os.path import exists, getsize, dirname, expanduser
import logging
from shutil import move
from time import sleep
import subprocess
from typing import Optional

import colored_logging as cl
from .timer import Timer

__author__ = "Gregory H. Halverson"

logger = logging.getLogger(__name__)

# Default values for download retries and wait time between retries
DEFAULT_DOWNLOAD_RETRIES = 3
DEFAULT_DOWNLOAD_WAIT_SECONDS = 60

class DownloadFailed(ConnectionError):
    """Custom exception for download failures."""
    pass

def download_file(
        URL: str, 
        filename: str, 
        retries: int = DEFAULT_DOWNLOAD_RETRIES, 
        wait_seconds: int = DEFAULT_DOWNLOAD_WAIT_SECONDS,
        capture_output: bool = True,
        show_command: bool = False) -> Optional[str]:
    """
    Download a file from a specified URL using wget, with support for retries and logging.

    Parameters:
        URL (str): The URL of the file to download.
        filename (str): The local path where the file should be saved.
        retries (int): The number of times to retry downloading the file in 
                       case of failure (default is 3).
        wait_seconds (int): The number of seconds to wait between retries 
                            (default is 60 seconds).

    Returns:
        Optional[str]: The path of the downloaded file if successful, 
                       otherwise raises a DownloadFailed exception.
                       
    Raises:
        DownloadFailed: If the download fails after the specified number of 
                        retries, or if the downloaded file is empty.
    """
    attempts = 0  # Initialize the number of attempts to zero

    # filename = expanduser(filename)  # Expand the user's home directory in the filename

    # Loop until the maximum number of attempts is reached
    while attempts < retries:
        try:
            # Check if the file already exists and is zero in size
            if exists(expanduser(filename)) and getsize(expanduser(filename)) == 0:
                logger.warning(f"Removing zero-size corrupted file: {filename}")
                os.remove(expanduser(filename))  # Remove the corrupted file

            # If the file already exists and is valid, log and return its name
            if exists(expanduser(filename)):
                logger.info(f"File already downloaded: {cl.file(filename)}")
                return filename

            # Log the download attempt
            logger.info(f"Downloading: {cl.URL(URL)} -> {cl.file(filename)}")
            directory = dirname(filename)  # Get the directory of the filename
            makedirs(directory, exist_ok=True)  # Create the directory if it doesn't exist

            # Prepare a partial filename for the download process
            partial_filename = f"{filename}.download"
            # Construct the wget command with netrc support for authentication
            command = [
                'wget', '-c', '--netrc', '-O', expanduser(filename), URL
            ]

            if show_command:
                logger.info(" ".join(command))  # Log the wget command

            # Start a timer to measure the download duration
            timer = Timer()
            # Execute the wget command and capture output
            result = subprocess.run(command, capture_output=capture_output, text=True)

            # Log the download completion time
            logger.info(f"Completed download in {cl.time(timer)} seconds: {cl.file(filename)}")

            # Check if the download was successful
            if result.returncode != 0 or not exists(partial_filename):
                raise DownloadFailed(f"Failed to download URL: {URL}, attempt {attempts + 1}")

            # Check if the downloaded file is zero in size
            if getsize(partial_filename) == 0:
                logger.warning(f"Removing zero-size corrupted file: {partial_filename}")
                os.remove(partial_filename)  # Remove the corrupted partial file
                raise DownloadFailed(f"Failed to download URL: {URL}, attempt {attempts + 1}")

            # Move the partial file to the final filename
            move(expanduser(partial_filename), expanduser(filename))

            # Confirm that the final file exists
            if not exists(expanduser(filename)):
                raise DownloadFailed(f"Failed to download file: {filename}, attempt {attempts + 1}")

            return filename  # Return the path of the successfully downloaded file

        except Exception as e:
            # Log the exception and the attempt number
            logger.exception(f"Error on attempt {attempts + 1}: {e}")
            logger.warning(f"Waiting for {wait_seconds} seconds before retrying...")
            sleep(wait_seconds)  # Wait before retrying the download
            attempts += 1  # Increment the attempt count

    # Raise an exception if all attempts fail
    raise DownloadFailed(f"Failed to download file after {retries} attempts: {URL}")
