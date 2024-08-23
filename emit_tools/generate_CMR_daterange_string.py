from typing import Union
from datetime import date, datetime, time
from dateutil import parser

from .constants import CMR_DATETIME_FORMAT

# based on https://github.com/nasa/EMIT-Data-Resources/blob/main/python/how-tos/How_to_find_EMIT_data_using_CMR_API.ipynb

def generate_CMR_daterange_string(start_date: Union[date, str], end_date: Union[date, str]) -> str:
    """
    Generates a date range string formatted for CMR (Common Metadata Repository) queries.

    Args:
        start_date (Union[date, str]): The start date of the range. Can be a date object or a string.
        end_date (Union[date, str]): The end date of the range. Can be a date object or a string.

    Returns:
        str: A string representing the date range in the format required by CMR.

    References:
        - https://github.com/nasa/EMIT-Data-Resources/blob/main/python/how-tos/How_to_find_EMIT_data_using_CMR_API.ipynb
    """
    if isinstance(start_date, str):
        start_date = parser.parse(start_date)

    if isinstance(end_date, str):
        end_date = parser.parse(end_date)

    start_time = datetime.combine(start_date, time(0, 0, 0))
    end_time = datetime.combine(end_date, time(23, 59, 59))
    CMR_daterange_string = start_time.strftime(CMR_DATETIME_FORMAT) + ',' + end_time.strftime(CMR_DATETIME_FORMAT)

    return CMR_daterange_string
