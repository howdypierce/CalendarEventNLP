#!/usr/bin/env python3

import urllib.parse
from datetime import *
import event_parser

def convert_date_time(d: date, t: time) -> str:
    """Converts a date and time to a UTC string appropriate for passing to
    Google Calendar.

    d must be a valid datetime.date; ValueError will be raised if it
    is None.

    If t is not None, the returned string will follow the format
    YYYYMMDDTHHMMSSZ (where the time has been converted from localtime
    into UTC). If t is None, the returned string will show just the
    date: YYYYMMDD.

    These formats are one of the ISO 8601 formats, but unfortunately
    not the ISO 9601 format returned by the Python .isoformat()
    function, so we can't use that.
    """
    if not d:
        raise ValueError("Must specify a date")

    if t:
        return datetime.combine(d, t).strftime("%Y%m%dT%H%M%S")
    else:
        return d.strftime("%Y%m%d")
    

def parse_to_google_calendar(raw: str,
                             default_duration: int = 30,
                             debug: bool = False):

    """Parse a natural language string to a Google calendar event URL.

    Returns a URL representing a Google calendar event as slightly
    documented at https://stackoverflow.com/questions/22757908/google-calendar
    -render-action-template-parameter-documentation

    See documentation for the parse() function for details on how the
    raw string is processed

    default_duration (in minutes) is the duration of the event, if
    only a start time (and not end time) can be determined from the
    input.
    """

    (st_date, end_date, st_time, end_time, title, loc) = event_parser.parse(raw, debug)

    if st_time is not None and end_time is None:
        end_time = st_time + timedelta(minutes = default_duration)

    anchor = "https://calendar.google.com/calendar/event?"

    start = convert_date_time(st_date, st_time)
    end = convert_date_time(st_date, end_time)
    
    params = { 'action' : 'TEMPLATE',
               'text' : title,
               'location' : loc,
               'dates' : f"{start}/{end}" }
    return (anchor + urllib.parse.urlencode(params))


