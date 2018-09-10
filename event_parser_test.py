#!/usr/bin/env python3
#
# event_parser_test.py: Test cases for event_parser.py
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


import event_parser as ep
from testdata import testdata


def test_parse_time_to_norm(raw: str, expect: str):
    res = ep.parse_time_to_norm(raw)
    assert res == expect, raw

# list of (input, expected output)
time_strings = [ ("8", "reltime:08:00:00"),
                 ("8:00", "reltime:08:00:00"),
                 ("8:00:00", "reltime:08:00:00"),
                 ("8a", "abstime:08:00:00"),
                 ("8:00a", "abstime:08:00:00"),
                 ("8:00:00a", "abstime:08:00:00"),
                 ("8p", "abstime:20:00:00"),
                 ("8:00p", "abstime:20:00:00"),
                 ("8:00:00p", "abstime:20:00:00"),
                 ("7:59:30p", "abstime:19:59:30"),
                 ("midnight", "abstime:00:00:00"),
                 ("noon", "abstime:12:00:00"),
                 ("7:60:30p", None),

                 ("2am", "abstime:02:00:00"),
                 ("2:15am", "abstime:02:15:00"),
                 ("2:00:00am", "abstime:02:00:00"),

                 ("2a.m.", "abstime:02:00:00"),
                 ("2:00a.m", "abstime:02:00:00"),
                 ("2 am", None),

                 ("123", "reltime:01:23:00"),
                 ("123a", "abstime:01:23:00"),
                 ("123p", "abstime:13:23:00"),
                 ("0600", "abstime:06:00:00"),
                 ("0630", "abstime:06:30:00"),
                 ("0660", None),
                 ("600", "reltime:06:00:00"),
                 ("630", "reltime:06:30:00"),
                 ("660", None),
                 ("1400", "abstime:14:00:00"),
                 ("1430", "abstime:14:30:00"),
                 ("1460", None),
                 ("1400p", None),
                 ("1400a", None),
                 ("1080p", None),
                 ("720p", "abstime:19:20:00"),
                 ("0000", "abstime:00:00:00"),
                 ("1200", "abstime:12:00:00"),
                 ("2400", None),
                 ("2500", None),

                 ("midnight", "abstime:00:00:00"),
                 ("noon", "abstime:12:00:00"),
                 ("000", None),

                 ("1o'clock", "reltime:01:00:00"),
                 ("1oclock", "reltime:01:00:00"),
                 ("11o'clock", "reltime:11:00:00"),
                 ("13o'clock", None),

                 # odd cases
                 ("0:00", "abstime:00:00:00"),
                 ("0:00:1", None),
                 ("10:1", None),
                 ("10:10", "reltime:10:10:00"),
                 ("13:10", "abstime:13:10:00"),
                 ("24", None),
                 ("10 ", None),
                 ("10:00 ", None),
                 (" 10:00", None),
                 ("-1:00", None),
                 ("1:-0", None),
                 ("0", None),
                 ("24:10", None) ]

for v in time_strings: test_parse_time_to_norm(*v)


def test_parse_date_to_norm(raw: str, expect: str):
    res = ep.parse_date_to_norm(raw)
    assert res == expect, raw

# list of (input, expected output)
date_strings = [ ("2014/5/3", "absdate:05/03/2014"),
                 ("2014/5/03", "absdate:05/03/2014"),
                 ("2014/05/03", "absdate:05/03/2014"),
                 ("1987-5-3", "absdate:05/03/1987"),
                 ("1987-5-03", "absdate:05/03/1987"),
                 ("1987-05-03", "absdate:05/03/1987"),
                 ("1959/01/01", "absdate:01/01/1959"),
                 ("1900/01/01", None),

                 ("10/9/1994", "absdate:10/09/1994"),
                 ("10/9/2044", "absdate:10/09/2044"),
                 ("1/1/2020", "absdate:01/01/2020"),
                 ("1/31/2020", "absdate:01/31/2020"),
                 ("1/32/2020", None),
                 ("12/12/2019", "absdate:12/12/2019"),
                 ("12/21/2999", None),
                 ("10-9-1994", "absdate:10/09/1994"),
                 ("10-9-2044", "absdate:10/09/2044"),
                 ("1-1-2020", "absdate:01/01/2020"),
                 ("1-31-2020", "absdate:01/31/2020"),
                 ("1-32-2020", None),
                 ("12-12-2019", "absdate:12/12/2019"),
                 ("12-21-2999", None),
                 ("1/31-2020", None),

                 ("1/31", "reldate:01/31"),
                 ("3/6", "reldate:03/06"),
                 ("2/0", None),
                 ("1/4", "reldate:01/04"),
                 ("0/1", None),
                 ("12/1", "reldate:12/01"),
                 ("12/31", "reldate:12/31"),
                 ("12/32", None),
                 ("13/1", None),

                 ("mon", "reldate:weekday:0"),
                 ("tue", "reldate:weekday:1"),
                 ("wed", "reldate:weekday:2"),
                 ("weds", "reldate:weekday:2"),
                 ("thur", "reldate:weekday:3"),
                 ("fri", "reldate:weekday:4"),
                 ("saturday", "reldate:weekday:5"),
                 ("sunday", "reldate:weekday:6"),

                 ("today", ep.today.strftime("absdate:%m/%d/%Y")),
                 ("tomorrow", ep.tomorrow.strftime("absdate:%m/%d/%Y")),
                 ("yesterday", ep.yesterday.strftime("absdate:%m/%d/%Y"))]

for v in date_strings: test_parse_date_to_norm(*v)


def test_parse(input_tuple) -> bool:
    """Test parse the input tuple, return results.

    Returns a tuple 
      (date_score, time_score, title_score, location_score, pass_fail)
    If the input was parsed perfectly, this tuple
    would be (2, 2, 1, 1, True).

    """

    raw = input_tuple[0]
    res = ep.parse(raw)

    # evaluate how we did
    date_score = int(res[0] == input_tuple[1]) + int(res[1] == input_tuple[2])
    time_score = int(res[2] == input_tuple[3]) + int(res[3] == input_tuple[4])
    title_score = int(res[4] == input_tuple[5])
    location_score = int(res[5] == input_tuple[6])
    
    total = date_score + time_score + title_score + location_score
    pass_fail = (total == 6)

    BOLD = '\033[1m'
    END = '\033[0m'

    if (not pass_fail):
        s = raw 
        for i in range(6):
            if res[i] != input_tuple[i+1]:
                s += f"|\033[1m{res[i]}\033[0m"
            else:
                s += f"|ok"
        print(s)

    return (date_score, time_score, title_score, location_score, pass_fail)


def run():
    date_success = 0
    time_success = 0
    title_success = 0
    location_success = 0
    full_success = 0
    for t in testdata:
        res = test_parse(t)
        if res[0] == 2: date_success += 1
        if res[1] == 2: time_success += 1
        if res[2] == 1: title_success += 1
        if res[3] == 1: location_success += 1
        if res[4]: full_success += 1

    print(f"Correctly parsed date: {date_success} time: {time_success} "
          f"title: {title_success} loc: {location_success} "
          f"full: {full_success} of {len(testdata)}")
       
run()


