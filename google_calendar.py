#!/usr/local/bin/python3
#
# google_calendar.py: Parse a natural language calendar event and
#    launch the Google Calendar "details" page
#
# Copyright (C) 2018 Cardinal Peak LLC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import sys
import urllib.parse
from datetime import time, date, timedelta, datetime
import subprocess
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

    See documentation for the parse_event() function for details on
    how the raw string is processed

    default_duration (in minutes) is the duration of the event, if
    only a start time (and not end time) can be determined from the
    input.

    """

    ret = event_parser.parse_event(raw, debug, log=True)
    (st_date, end_date, st_time, end_time, title, loc) = ret

    if st_date is None:
        st_date = event_parser.today
        end_date = event_parser.today

    if st_time is not None and end_time is None:
        st_dt = datetime.combine(st_date, st_time)
        end_dt = st_dt + timedelta(minutes=default_duration)
        end_date = end_dt.date()
        end_time = end_dt.time()

    anchor = "https://calendar.google.com/calendar/event?"

    start = convert_date_time(st_date, st_time)
    end = convert_date_time(end_date, end_time)

    params = {'action': 'TEMPLATE',
              'text': title,
              'dates': f"{start}/{end}"}
    if loc:
        params['location'] = loc

    return (anchor + urllib.parse.urlencode(params))


if __name__ == '__main__':

    def usage():
        bn = os.path.basename(sys.argv[0])
        usage_msg = ("Usage: {exe_name} Event Text"
                     "\n")
        print(usage_msg.format(exe_name=bn))
        sys.exit(1)

    if len(sys.argv) < 2:
        usage()

    s = " ".join(sys.argv[1:])
    url = parse_to_google_calendar(s)
    subprocess.call(["open", url])
