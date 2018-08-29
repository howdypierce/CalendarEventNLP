#

import nltk
import re
import sys
from datetime import *
from dateutil import relativedelta
from etoken import *
from spelled_numbers import handle_spelled_number
from testdata import testdata

meridian_txt = ["a", "am", "a.m.", "a.m", "p", "pm", "p.m.", "p.m"]
day_txt = ["day", "days", "d"]
week_txt = ["week", "weeks", "wk"]
month_txt = ["month", "months", "mon"]
minute_txt = ["min", "mins", "minute", "minutes"]
hour_txt = ["hr", "hrs", "hour", "hours", "h"]

weekday_to_num = {"monday": 0, "mon": 0, "mo": 0,
                  "tuesday": 1, "tue": 1, "tues": 1, "tu": 1,
                  "wednesday": 2, "wed": 2, "weds": 2,
                  "thursday": 3, "thu": 3, "thur": 3, "thurs": 3, "th": 3,
                  "friday": 4, "fri": 4, "fr": 4,
                  "saturday": 5, "sat": 5,
                  "sunday": 6, "sun": 6}

month_to_num = {"january": 1, "jan": 1, "february": 2, "feb": 2,
                "march": 3, "mar": 3, "april": 4, "apr": 4, "may": 5,
                "june": 6, "jun": 6, "july": 7, "jul": 7,
                "august": 8, "aug": 8, "september": 9, "sept": 9, "sep": 9,
                "october": 10, "oct": 10, "november": 11, "nov": 11,
                "december": 12, "dec": 12}

today = date.today()
tomorrow = today + timedelta(days=1)
yesterday = today - timedelta(days=1)

# if 4-digit years are specified, they must fall in this range
year_range = [1901, 2099]

# regexps to parse for time
ampm       = r"((?:[ap]m?)|(?:[ap]\.?m\.?))"  # a, am, a.m.
timespec   = r"(\d{1,2}):(\d{2})(:\d{2})?" + ampm + "?"  # hh:mm[:ss][am]
hourspec_m = r"(\d{1,2})" + ampm          # hham, hh in range 1..12
hourspec   = r"(\d{1,2})" + ampm + "?"    # hh[am], hh in range 1..23
milspec    = r"(\d{2})(\d{2})"            # hhmm, all 4 digits present
nocolon_m  = r"(\d{1,2})(\d{2})" + ampm   # hhmmam, 1 or 2 h digits
nocolon    = nocolon_m + "?"              # hhmm[am], 1 or 2 h digits
oclspec    = r"(\d{1,2})o'?clock"  # hho'clock, hh in range 1..12
mid_noon   = r"(midnight)|(noon)"

# following matches strings that are unambiguously times
re_time_certain = ( "(" + timespec + ")|"
                    "(" + hourspec_m + ")|"
                    "(" + nocolon_m + ")|"
                    "(" + oclspec + ")|"
                    "(" + mid_noon + ")" )

# more permissive, anything that might be a time; must be a superset
# of re_time_certain
re_time_possible = ( "(" + timespec + ")|"
                     "(" + hourspec + ")|"
                     "(" + nocolon + ")|"
                     "(" + oclspec + ")|"
                     "(" + mid_noon + ")" )

def parse_time_to_norm(s: str) -> str:
    """Attempt to parse a string into a time.

    If the input string is a time in one of the forms:
        hh:mm[:ss]am (where seconds and am/pm can be omitted)
        hham (where am/pm can be omitted)
        xxxx (military time, 3 or 4 digits)
        hho'clock (with or without the apostrophe)
        abstime:hour:minute:second
        reltime:hour:minute:second
        midnight | noon

    return a string of one of the forms

       "abstime:hour:minute:second", with hour in the range 0-23, if
          we can determine for certain the am/pm 

       "reltime:hour:minute:second", with hour in the range 1-12, if we
         cannot determine the am/pm

    otherwise return None
    """

    # special cases
    if s == "midnight":
        return "abstime:00:00:00"
    if s == "noon":
        return "abstime:12:00:00"
    if s == "000":
        return None
    if re.match(r"^(rel)|(abs)time:\d{2}:\d{2}:\d{2}$", s):
        return s

    hour = None
    minutes = None
    seconds = 0

    is_pm = False
    meridian_specified = False

    m = re.fullmatch(timespec, s)
    if m:
        hour = int(m.group(1))
        minutes = int(m.group(2))
        if (m.group(3)):
            seconds = int(m.group(3)[1:])
        if m.group(4):
            meridian_specified = True
            if m.group(4)[0] == "p":
                is_pm = True
        else:  # special case of hour being specified as 0 or 00
            if m.group(1) in ["0", "00"]:
                meridian_specified = True
                is_pm = False
            
    if hour is None:
        m = re.fullmatch(hourspec, s)
        if m and 1 <= int(m.group(1)) <= 23:
            hour = int(m.group(1))
            minutes = 0
            if m.group(2):
                if (hour > 12):
                    hour = None  
                else:
                    meridian_specified = True
                    if m.group(2)[0] == "p":
                        is_pm = True

    if hour is None:
        m = re.fullmatch(milspec, s)
        if m:
            hour = int(m.group(1))
            minutes = int(m.group(2))
            meridian_specified = True

    if hour is None:
        m = re.fullmatch(nocolon, s)
        if m:
            hour = int(m.group(1))
            minutes = int(m.group(2))
            if m.group(3):
                if (hour > 12):
                    hour = None  
                else:
                    meridian_specified = True
                    if m.group(3)[0] == "p":
                        is_pm = True

    if hour is None:
        m = re.fullmatch(oclspec, s)
        if m and 1 <= int(m.group(1)) <= 12:
            hour = int(m.group(1))
            minutes = 0
            meridian_specified = False

    if hour is None:
        return None
    
    if (not 0 <= hour <=23):
        return None
    if (not 0 <= minutes <= 59):
        return None
    if (not 0 <= seconds <= 59):
        return None

    if (meridian_specified and is_pm and hour < 12):
        hour += 12

    if (meridian_specified or hour > 12):
        return f"abstime:{hour:02}:{minutes:02}:{seconds:02}"
    else:
        return f"reltime:{hour:02}:{minutes:02}:{seconds:02}"

# TODO: move inline testing to a real test harness
def test_parse_time_to_norm(raw: str, expect: str):
    res = parse_time_to_norm(raw)
    assert res == expect, raw

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

def parse_date_to_norm(s: str) -> str:
    """Attempt to parse a string into a date.

    If the input string is a date in one of the forms:
        yyyy/mm/dd or yyyy-mm-dd (year must be 4 digits)
        mm/dd/yyyy or mm-dd-yyyy (where year can be omitted, or 2 or 4 digits)
        a weekday, including common abbreviations
        today | tomorrow | yesterday
       "absdate:month/day/year", if we know the year for certain
       "reldate:(stuff)", if we cannot determine the year 

    return a string of one of the normalized date forms

       "absdate:month/day/year", if we know the year for certain
       "reldate:month/day", if we cannot determine the year 
       "reldate:weekday:(num)",  (e.g., "on Thursday") 
       "reldate:monthday:(num)", (e.g., "on the 21st")

    otherwise return None
    """

    if (re.match(r"^reldate:", s) or
        re.fullmatch(r"absdate:\d{2}/\d{2}/\d{4}", s)):
        return s

    # first parse weekdays
    if s in weekday_to_num:
        num = weekday_to_num[s]
        return f"reldate:weekday:{num}"

    # today, tomorrow
    if s == "today": return today.strftime("absdate:%m/%d/%Y")
    if s == "tomorrow": return tomorrow.strftime("absdate:%m/%d/%Y")
    if s == "yesterday": return yesterday.strftime("absdate:%m/%d/%Y")

    year = None
    month = None
    day = None

    # match date: yyyy/mm/dd. must be 4 digit yr and year must be specified
    m = re.fullmatch(r"(\d{4})(?P<sep>[-/])(\d{1,2})(?P=sep)(\d{1,2})", s)
    if m:
        year = int(m.group(1))
        month = int(m.group(3))
        day = int(m.group(4))

    # match date: mm/dd/yyyy or mm/dd/yy, year may be omitted
    mdyspec = r"(\d{1,2})(?P<sep>[-/])(\d{1,2})((?P=sep)(?:\d{2}|\d{4}))?"
    m = re.fullmatch(mdyspec, s)
    if m:
        month = int(m.group(1))
        day = int(m.group(3))
        if m.group(4):
            year=int(m.group(4)[1:])
            # arbitrarily: 2-digit years interpreted as within [-50,+49] of today
            if year < 100:
                year += 2000
                if year > today.year + 49:
                    year -= 100

    if (month is None or day is None or not 1 <= month <= 12 or
        not 1 <= day <= 31):
        return None

    if year is None:
        return f"reldate:{month:02}/{day:02}"

    if min(year_range) <= year <= max(year_range):
        return f"absdate:{month:02}/{day:02}/{year:04}"

    return None


def test_parse_date_to_norm(raw: str, expect: str):
    res = parse_date_to_norm(raw)
    assert res == expect, raw

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

                 ("today", today.strftime("absdate:%m/%d/%Y")),
                 ("tomorrow", tomorrow.strftime("absdate:%m/%d/%Y")),
                 ("yesterday", yesterday.strftime("absdate:%m/%d/%Y"))]

for v in date_strings: test_parse_date_to_norm(*v)

def parse_time_date_range(tok: EToken, lookahead: EToken) -> list:
    """First attempt to parse a token to a time or date.  

    Handles the following cases:

    - If this single token appears to be of the form (time)-(time) or
      (date)-(date), where we know with high confidence that this is
      in fact a time range or date range, then return three tokens:
      "start" "until" "end"

    - If this single token appears with high confidence to be a single
      time or date, return a token representing that

    - If the single token is a weekday name or one of the words
      'today', 'tomorrow', or 'yesterday', return a token representing
      that

    - For time ranges and single times, also considers a lookahead
      token, which could be a meridian ("am", "AM", "a.m.", etc) or
      the word "o'clock"

    If no match, return None.
    """

    append_second = ""
    ignore_lookahead = False

    # time ranges

    m = re.fullmatch(f"(?P<first>{re_time_certain})-(?P<second>{re_time_possible})",
                     tok.val)
    if not m:
        m = re.fullmatch(f"(?P<first>{re_time_possible})-(?P<second>{re_time_certain})",
                         tok.val)

    # handle case where we've matched a time, but the lookahead is a meridian
    if m and lookahead.match(meridian_txt):
        append_second = lookahead.val
        ignore_lookahead = True

    if not m:
        m = re.fullmatch(f"(?P<first>{milspec})-(?P<second>{milspec})",
                         tok.val)

    if not m and lookahead.match(meridian_txt):
        m = re.fullmatch(f"(?P<first>{re_time_possible})-(?P<second>{re_time_possible})",
                         tok.val)
        append_second = lookahead.val
        ignore_lookahead = True

    if m:
        st = parse_time_to_norm(m.group("first"))
        end = parse_time_to_norm(m.group("second") + append_second)
        if st is not None and end is not None:
            if ignore_lookahead:
                lookahead.sem = "IGN"
            return [EToken(st, "TIME", "ST_TIME"),
                    EToken("UNTIL", ":", "IGN"),
                    EToken(end, "TIME", "ST_TIME")]

    # parse standalone time
    if lookahead.match(meridian_txt + ["o'clock", "oclock"]):
        m = re.fullmatch(re_time_possible, tok.val)
        if m: 
            val = parse_time_to_norm(tok.val + lookahead.val)
            if val:
                lookahead.sem = "IGN"
                return [EToken(val, "TIME", "TIME")]

    m = re.fullmatch(re_time_certain, tok.val)
    if m:
        val = parse_time_to_norm(tok.val)
        if val:
            return [EToken(val, "TIME", "TIME")]


    # date range
    datespec = r"\d{1,2}/\d{1,2}(?:/(?:\d{2}|\d{4}))?" # mm/dd/yy or mm/dd/yyyy
    datespec_yfirst = r"\d{4}/\d{1,2}/\d{1,2}" # yyyy/mm/dd
    m = re.match(f"^({datespec})-({datespec})$", tok.val)
    if m:
        st = parse_date_to_norm(m.group(1))
        end = parse_date_to_norm(m.group(2))
        if st is not None and end is not None:
            return [EToken(st, "DATE", "ST_DATE"),
                    EToken("UNTIL", ":", "IGN"),
                    EToken(end, "DATE", "END_DATE")]
        
    m = re.match(f"^({datespec_yfirst})-({datespec_yfirst})$", tok.val)
    if m:
        st = parse_date_to_norm(m.group(1))
        end = parse_date_to_norm(m.group(2))
        if st is not None and end is not None:
            return [EToken(st, "DATE", "ST_DATE"),
                    EToken("UNTIL", ":", "IGN"),
                    EToken(end, "DATE", "END_DATE")]

    m = re.match(f"^({datespec})|({datespec_yfirst})$", tok.val)
    if m:
        val = parse_date_to_norm(tok.val)
        if val: return [EToken(val, "DATE", "DATE")]

    # we have to be conservative with dates specified using hyphens,
    # because they could mean a lot of different things. For now, it's
    # only a date if it is dd-mm-yyyy or dd-mm-yy, or yyyy-dd-mm
    m = re.match(r"^(\d{1,2}|\d{4})-(\d{1,2})-(\d{2}|\d{4})$", tok.val)
    if m:
        val = parse_date_to_norm(tok.val)
        if val: return [EToken(val, "DATE", "DATE")]

    # handle spelled weekdays and special strings
    if tok.match(weekday_to_num) or tok.match(["today","tomorrow","yesterday"]):
        val = parse_date_to_norm(tok.val)
        if val: return [EToken(val, "DATE", "DATE")]

    return None


def parse_spelled_date(t_mon: EToken, t_day: EToken, t_year: EToken) -> str:
    """If possible, parse the three tokens into a date normal form.

    We have a possible date, with 2 or 3 tokens:
       t_mon - a spelled out month
       t_day - a day, either CD or OD form
       t_year - either None, or a possible year in CD form

    If possible, parse this into a date normal form (see above for
    what this means), and return it.

    Otherwise return None.
    """
    month = month_to_num[t_mon.val]
    day = int(t_day.val)
    if not 1 <= day <= 31:
        return None

    if not t_year:
        return f"reldate:{month:02}/{day:02}"

    m = re.fullmatch(r"\d{4}", t_year.val)
    if m and min(year_range) <= int(m.group(0)) <= max(year_range):
        year = int(m.group(0))
        return f"absdate:{month:02}/{day:02}/{year:04}"

    return None


def collapse_expand_tokens(token_list: list) -> list:
    """Collapse and expand the token list as the first phase of processing.

    On input, look at the string of tokens at the head of token_list.
    Return a list containing 0-N output tokens.

    Makes the following substitutions:

     1) Concatenates a possessive token with the preceeding noun, so
        for instance the token stream "Doug/NNP" and "'s/POS" will be
        turned into the single token "Doug's/NNP"

     5) For a string of tokens following the form
           (time) in the ("morning" | "afternoon" | "evening")
           (time) at night
        returns a single token representing the time.

     6) For the string of tokens
           next (weekday)
        returns a single token representing the date.

     2) For a single token which appears to be of the form
        (time)-(time) or (date)-(date), return three tokens: (start)
        (UNTIL) (end), with "start" and "end" simplified for future
        processing. (*)

     3) For two tokens which appear to be of the form (time) (am/pm),
        returns a single token representing the time. (*)

     4) For a single token which can be unambiguously parsed as either
        a time or date, returns a single token representing the
        time/date in processed form (*)

     7) Collapses the following strings of date tokens into a single
        token representing the date:
           (day) (spelled-month) (year)
           (day) (spelled-month)
           (spelled-month) (day)
           (spelled-month) (day) (comma) (year)

     8) Collapses the two token string "the" (OD) (as in "the 21st")
        into a single token representing this as a date.

     (* - these substitutions handled by parse_time_date_range)

    """
    t = padded(token_list, 10)

    # ignore stuff we've already decided to ignore
    if (t[0].sem == "IGN"): return []

    # concatenate possessives
    if t[0].match(pos="NNP") and t[1].match(pos="POS"):
        t[0].orig += t[1].orig
        t[0].val += t[1].val
        t[1].sem = "IGN"
        return [t[0]]

    # (CD) ((in) (the) (morning | afternoon | evening)) | ((at) (night))
    if t[0].match(pos="CD"):
        append = ""
        if (t[1].match("in", "IN") and t[2].match("the", "DT") and
            t[3].match(["morning", "afternoon", "evening"])):
            if t[3].match("morning"):
                append = "am"
            else:
                append = "pm"
            t[1].sem = "IGN"
            t[2].sem = "IGN"
            t[3].sem = "IGN"
        elif (t[1].match("at", "IN") and t[2].match("night")):
            append = "pm"
            t[1].sem = "IGN"
            t[2].sem = "IGN"
        if append != "":
            t[0].val += append
            t[0].sem = "TIME"
            t[0].pos = "TIME"
            return [t[0]]

    # (next) (weekday)
    if (t[0].match("next", "JJ") and t[1].match(weekday_to_num)):
        val = parse_date_to_norm(t[1].val)
        if val:
            t[1].sem = "IGN"
            return [EToken(val, "DATE", "DATE")]

    # time/date range
    res = parse_time_date_range(t[0], t[1])
    if res: return res

    # (month) (comma or THE - optional) (OD or CD) (comma - optional)
    # (CD - optional - year)
    d = 1
    if (t[d].match(",", pos=",") or t[d].match("the", "DT")): d += 1
    if (t[0].match(month_to_num) and t[d].match(pos=["CD", "OD"])):
        y = d+1
        res = None
        if t[y].match(",", pos=","): y += 1
        if t[y].match(pos="CD"):
            res = parse_spelled_date(t[0], t[d], t[y])
            end_tok = y
        if res is None:
            res = parse_spelled_date(t[0], t[d], None)
            end_tok = d
        if res:
            for i in range(1, end_tok+1): t[i].sem = "IGN"
            return [EToken(res, "DATE", "DATE")]

    # (THE - opt) (OD | CD day) (comma | OF - opt) (month)
    # (comma - opt) (CD - opt year)
    d = 0
    if (t[d].match("the", "DT")): d += 1
    m = d+1
    if (t[m].match(",", pos=",") or t[m].match("of", pos="IN")): m += 1
    if (t[d].match(pos=["CD", "OD"]) and t[m].match(month_to_num)):
        y = m+1
        res = None
        if t[y].match(",", pos=","): y += 1
        if t[y].match(pos="CD"):
            res = parse_spelled_date(t[m], t[d], t[y])
            end_tok = y
        if res is None:
            res = parse_spelled_date(t[m], t[d], None)
            end_tok = m
        if res:
            for i in range(1, end_tok+1): t[i].sem = "IGN"
            return [EToken(res, "DATE", "DATE")]

    # (the) (OD)
    if (t[0].match("the", "DT") and t[1].match(pos="OD")):
        t[1].sem="IGN"
        return [EToken(f"reldate:monthday:{t[1].val}", "DATE", "DATE")]

    return [t[0]]


def date_from_day(day_num: int, anchor: date) -> str:
    """When someone says "meet on the 3rd", returns the next such day
    after the anchor, as a datetime.date
    """
    if anchor.day < day_num:
        return anchor.replace(day=day_num)
    if anchor.month == 12:
        return date(anchor.year + 1, 1, day_num)
    return date(anchor.year, anchor.month+1, day_num)


def norm_to_date(t: EToken, hint_date: date = today) -> date:
    """Convert a token containing a normalized date into the corresponding
    datetime.date.

    hint_date (default: today) is a minimum. If the token is a
    reldate, then it will be adjusted to come after hint_date.
    """
    assert(t.pos == "DATE")
    m = re.fullmatch(r"absdate:(\d{2})/(\d{2})/(\d{4})", t.val)
    if m:
        return date(int(m.group(3)), int(m.group(1)), int(m.group(2)))

    m = re.fullmatch(r"reldate:weekday:(\d)", t.val)
    if m:
        delta = int(m.group(1)) - hint_date.weekday()
        if delta <= 0:
            delta += 7
        return hint_date + timedelta(days=delta)

    m = re.fullmatch(r"reldate:monthday:(\d{1,2})", t.val)
    if m:
        return date_from_day(int(m.group(1)), hint_date)

    m = re.fullmatch(r"reldate:(\d{2})/(\d{2})", t.val)
    if not m:
        assert False, t.val

    month = int(m.group(1))
    day = int(m.group(2))
    trial_date = date(hint_date.year, month, day)
    if (trial_date < hint_date):
        return date(hint_date.year + 1, month, day)
    else:
        return trial_date


def norm_to_time(t: EToken, hint: time = None) -> time:
    """Convert a token containing a normalized time into the corresponding
    datetime.time.

    hint (default: noon) is a target time. If the token is a reltime,
    its am/pm will be interpreted so as to get as close as possible to
    hint.
    """
    assert(t.pos == "TIME")
    m = re.fullmatch(r"(abs|rel)time:(\d{2}):(\d{2}):(\d{2})", t.val)
    if not m:
        assert False, t

    if hint is None: hint = time(12)

    hour = int(m.group(2))
    minute = int(m.group(3))
    second = int(m.group(4))
    
    if m.group(1) == "rel":
        assert 1 <= hour <= 12, t
        am_dist = abs(hour - hint.hour)
        pm_dist = abs(12 + hour - hint.hour)
        if pm_dist < am_dist: hour += 12

    return time(hour, minute, second)


def match_until(t: EToken) -> bool:
    """Returns true if this token is a form of 'until' or 'to'."""
    return (t.match(["to", "TO"]) or t.match(["-", ":"]) or
            t.match(["until", "til", "till", "thru", "through"]))
    

def parse_phrase(tok_list: list): 
    """Parse for multi-word phrases.

    When called, examine the provided string of tokens. The list is
    guaranteed to have one element -- e.g., t[0] is guaranteed to
    exist. Other tokens might not be present.
    """

    t = padded(tok_list, 10)

    # (from - optional) (time | CD) (until) (time | CD)
    m = 0
    if t[0].match("from", "IN"): m += 1
    if (t[m].match(pos=["TIME", "CD"]) and match_until(t[m+1]) and
        t[m+2].match(pos=["TIME", "CD"])):
        st = parse_time_to_norm(t[m].val)
        end = parse_time_to_norm(t[m+2].val)
        if st is not None and end is not None:
            if t[0].match("from"): t[0].sem = "IGN"
            t[m].val = st
            t[m].sem = "ST_TIME"
            t[m].pos = "TIME"
            t[m+1].sem = "IGN"
            t[m+2].val = end
            t[m+2].sem = "END_TIME"
            t[m+2].pos = "TIME"
            return

    # (from - optional) (date) (until) (date | CD)
    m = 0
    if t[0].match("from", "IN"): m += 1
    if (t[m].match(pos="DATE") and match_until(t[m+1]) and
        t[m+2].match(pos=["DATE", "CD", "OD"])):
        st = parse_date_to_norm(t[m].val)
        if t[m+2].match(pos=["CD", "OD"]):
            end = f"reldate:monthday:{t[m+2].val}"
        else:
            end = parse_date_to_norm(t[m+2].val)
        if st is not None and end is not None:
            if t[0].match("from"): t[0].sem = "IGN"
            t[m].val = st
            t[m].sem = "ST_DATE"
            t[m].pos = "DATE"
            t[m+1].sem = "IGN"
            t[m+2].val = end
            t[m+2].sem = "END_DATE"
            t[m+2].pos = "DATE"
            return

    # (on) (date)
    if (t[0].match("on", "IN") and t[1].match(pos="DATE")):
        st = parse_date_to_norm(t[1].val)
        if st is not None:
            t[0].sem = "IGN"
            t[1].val = st
            t[1].sem = "ST_DATE"
            return

    # (in)? (a or CD) (week | month | day)  (from (date) - optional)
    m = 0
    if t[0].match("IN", "IN"): m += 1
    if ((t[m].match("a", "DT") or t[m].match(pos="CD")) and
        t[m+1].match(week_txt + month_txt + day_txt)):
        if t[m].pos == "DT":
            num = 1
        else:
            num = int(t[m].val)
        if (t[m+2].match("from", "IN") and t[m+3].match(pos="DATE")):
            anchor = norm_to_date(t[m+3])
            end_tok = m+3
        else:
            anchor = today
            end_tok = m+1

        if (t[m+1].match(week_txt)):
            dt = anchor + timedelta(weeks=num)
        elif (t[m+1].match(month_txt)):
            dt = anchor + relativedelta.relativedelta(months=num)
        else:   # days
            dt = anchor + timedelta(days=num)

        for i in range(0, end_tok+1):
            t[i].sem = "IGN"

        t[m].val = dt.strftime("absdate:%m/%d/%Y")
        t[m].pos = "DATE"
        t[m].sem = "DATE"
        return

    # (DT or CD) (week | month | day) (after) (date)
    if (t[0].match(pos=["DT","CD"]) and
        t[1].match(week_txt + month_txt + day_txt) and
        t[2].match("after", "IN") and t[3].match(pos="DATE")):
        if t[0].pos == "DT":
            num = 1
        else:
            num = int(t[0].val)
        anchor = norm_to_date(t[3])
        
        if (t[1].match(week_txt)):
            dt = anchor + timedelta(weeks=num)
        elif (t[1].match(month_txt)):
            dt = anchor + relativedelta.relativedelta(months=num)
        else:   # days
            dt = anchor + timedelta(days=num)

        for i in range(0, 4):
            t[i].sem = "IGN"
        t[1].val = dt.strftime("absdate:%m/%d/%Y")
        t[1].pos = "DATE"
        t[1].sem = "DATE"
        return

    # (in) (CD) (minutes | hours) - return both date and time
    if (t[0].match("in", "IN") and t[1].match(pos="CD") and
        t[2].match(minute_txt + hour_txt)):
        val = float(t[1].val)
        if t[2].match(hour_txt): val *= 60
        dt = datetime.now() + timedelta(minutes=int(val))
        t[0].val = dt.strftime("absdate:%m/%d/%Y")
        t[0].pos = "DATE"
        t[0].sem = "ST_DATE"
        t[1].val = dt.strftime("abstime:%H:%M:00")
        t[1].pos = "TIME"
        t[1].sem = "ST_TIME"
        t[2].sem = "IGN"
        return

    # (for) (CD) (minutes | hours) - duration
    if (t[0].match("for", "IN") and t[1].match(pos="CD") and 
        t[2].match(minute_txt + hour_txt)):
        val = float(t[1].val)
        if t[2].match(hour_txt): val *= 60
        t[0].sem = "IGN"
        t[1].val = str(int(val))
        t[1].pos = "TIME"
        t[1].sem = "DURATION"
        t[2].sem = "IGN"
        return

    # (at|in) (a location phrase)
    #
    # This was originally more complicated and less accurate. For our
    # purposes, a location phrase can (1) optional start with DT, PRP,
    # PRP$; and (2) is any consecutive run of nouns, adjectives, CD,
    # OD, and comma. HOWEVER, the location phrase MUST have at least
    # one noun or adjective; if not don't trigger this rule
    noun_pos = ["NN", "NNS", "NNP", "NNPS"]
    adjective_pos = ["JJ", "JJR", "JJS"]
    na_pos = noun_pos + adjective_pos
    loc_pos = noun_pos + adjective_pos + [",", "CD", "OD"]
    n = 1
    if t[1].match(pos=["DT", "PRP", "PRP$"], sem="-"): n += 1
    if (t[0].match(["at","in"], "IN") and t[n].match(pos=loc_pos, sem="-")):
        while t[n].match(pos=loc_pos, sem="-"):
            n += 1
        # n now points to one past the end token

        # see if we have at least one noun/adj
        na_count=0
        for i in range(1, n):
            if t[i].match(pos=na_pos): na_count += 1

        if na_count > 0:
            t[0].sem = "IGN"
            for i in range(1, n):
                t[i].sem = "LOCATION"
            # If the last token in the noun phrase is a comma, ignore it
            if t[n-1].match(pos=","): t[n-1].sem = "IGN"
            return
        
    # (at) (CD) (CD), try it as a time ("at seven thirty")
    if (t[0].match("at", "IN") and t[1].match(pos="CD") and
        t[2].match(pos="CD")):
        st = parse_time_to_norm(f"{t[1].val}:{t[2].val}")
        if st is not None:
            t[0].sem = "IGN"
            t[1].val = st
            t[1].sem = "ST_TIME"
            t[1].pos = "TIME"
            t[2].sem = "IGN"

    # (at) (time or CD)
    if (t[0].match("at", "IN") and t[1].match(pos=["TIME", "CD"])):
        st = parse_time_to_norm(t[1].val)
        if st is not None:
            t[0].sem = "IGN"
            t[1].val = st
            t[1].sem = "ST_TIME"
            t[1].pos = "TIME"
            return


def find_default_time_for_event(title_toks: list) -> time:
    """Suggest a default start time, based on the title."""
    times = {"dinner": time(18),
             "pizza": time(19),
             "fondue": time(18),
             "lunch": time(12),
             "breakfast": time(7,30),
             "bfast": time(7,30),
             "coffee": time(10),
             "beer": time(17),
             "beers": time(17),
             "evening": time(20),
             "night": time(22),
             "morning": time(6),
             "afternoon": time(15) }

    for t in title_toks:
        if t.match(times):
            return times[t.val]
    return None


def clean_punctuation(s: str) -> str:
    """Clean up the punctuation for title and location strings.

    - Remove a leading space ahead of comma, period, !, apostrophe
    - remove a leading comma or period
    - remove a trailing comma or period
    - turn `` and '' into double quotes

    Return the cleaned-up string
    """
    s = re.sub(" ([,.!'])", r"\1", s)
    s = re.sub(" `` ", " \"", s)
    s = re.sub("''", "\"", s)
    s = re.sub("^[,.] ", "", s)
    s = re.sub("[,.]$", "", s)
    return s


def compute_dates_and_times(d: dict) -> tuple:
    """Given the processed tokens, compute dates and times.

    Returns tuple (st_date, end_date, st_time, end_time)"""

    # sometimes start/end date or time was not specified, but we have
    # multiple generic date or time tokens; in this case the first is
    # the start and the second, if present, is the end
    if "ST_DATE" not in d and "DATE" in d and len(d["DATE"]) > 0:
        d["ST_DATE"] = [d["DATE"][0]]
        d["DATE"] = d["DATE"][1:]

    if "END_DATE" not in d and "DATE" in d and len(d["DATE"]) > 0:
        d["END_DATE"] = [d["DATE"][0]]
        d["DATE"] = d["DATE"][1:]

    if "ST_TIME" not in d and "TIME" in d and len(d["TIME"]) > 0:
        d["ST_TIME"] = [d["TIME"][0]]
        d["TIME"] = d["TIME"][1:]

    if "END_TIME" not in d and "TIME" in d and len(d["TIME"]) > 0:
        d["END_TIME"] = [d["TIME"][0]]
        d["TIME"] = d["TIME"][1:]

    st_date = None
    end_date = None
    st_time = None
    end_time = None
    default_time = None

    if "ST_DATE" in d:
        st_date = norm_to_date(d["ST_DATE"][0])

    if "END_DATE" in d:
        end_date = norm_to_date(d["END_DATE"][0], st_date)

    if "ST_TIME" in d:
        # If the end time is absolute and the start time is relative,
        # evaluate end first so that we can provide end as a hint to
        # start. Otherwise do them in the normal order.
        if (d["ST_TIME"][0].val.startswith("reltime:") and "END_TIME" in d and
            d["END_TIME"][0].val.startswith("abstime:")):
            end_time = norm_to_time(d["END_TIME"][0])
            st_time = norm_to_time(d["ST_TIME"][0], end_time)
        else:
            if "TITLE" in d:
                default_time = find_default_time_for_event(d["TITLE"])
            st_time = norm_to_time(d["ST_TIME"][0], default_time)

    if "END_TIME" in d and end_time is None:
        end_time = norm_to_time(d["END_TIME"][0], st_time)
        
    if st_time is not None and end_time is None and "DURATION" in d:
        anchor = today
        dur = int(d["DURATION"][0].val)   # in minutes
        if st_date is not None: anchor = st_date
        dt = datetime.combine(anchor, st_time) + timedelta(minutes=dur)
        if st_date is not None: end_date = dt.date() 
        end_time = dt.time()

    return (st_date, end_date, st_time, end_time)


def parse(raw, debug = False):
    """Parse the raw string.

    Returns tuple (start date, end date, start time, end time, title, location)
    """

    if (debug):
        print(f"parsing raw phrase: {raw}")

    # tokenize our input
    tokenized = nltk.word_tokenize(raw)
    temp_list = []
    for t in nltk.pos_tag(tokenized):
        tok = EToken(*t)
        handle_spelled_number(tok)
        if (tok.val == "@"): tok = EToken("at", "IN")
        temp_list.append(tok)

    if (debug):
        print(f"After tokenization: {temp_list}")

    # First pass: collapse / expand
    token_list = []
    for i in range(len(temp_list)):
        token_list.extend(collapse_expand_tokens(temp_list[i:]))

    if (debug):
        print(f"Before parsing for phrases: {token_list}")

    # Second pass: parse for phrases
    for i in range(len(token_list)):
        parse_phrase(token_list[i:])

    if (debug):
        print(f"after phrase parsing: {token_list}")

    # ignore some remaining tokens, such as "is"
    for t in token_list:
        if t.match("is", sem="-"):
            t.sem = "IGN"

    # assume all unknown tokens are title
    for t in token_list:
        if t.sem == "-": t.sem = "TITLE"

    # process tokens into a dict of tokens
    d = {}
    for t in token_list:
        if t.sem not in d:
            d[t.sem] = [t]
        else:
            d[t.sem].append(t)

    if (debug):
        print(f"dict: {d}")

    if "TITLE" in d:
        title = clean_punctuation(" ".join([t.orig for t in d["TITLE"]]))
    else:
        title = None

    if "LOCATION" in d:
        location = clean_punctuation(" ".join([t.orig for t in d["LOCATION"]]))
    else:
        location = None
        
    (st_date, end_date, st_time, end_time) = compute_dates_and_times(d)

    ret = (st_date, end_date, st_time, end_time, title, location)

    if (debug):
        print(f"Returning: {ret}")

    return ret


def remove_possessives(tok: list) -> list:
    """Returns a POS-tagged list, collapsing the possessives"""
    ret = []
    for i in range(len(tok)):
        if tok[i][1] == 'POS':
            continue
        if i+1 < len(tok) and tok[i+1][1] == 'POS':
            ret.append( (tok[i][0] + "'s", tok[i][1]) )
        else:
            ret.append(tok[i])
    return ret


def test_parse(input_tuple) -> bool:
    """Test parse the input tuple, return results.

    Returns a tuple (date_score, time_score, metadata_score). If the
    input was parsed perfectly, this tuple would be (2, 2, 2).
    """

    raw = input_tuple[0]
    res = parse(raw)

    # evaluate how we did
    date_score = int(res[0] == input_tuple[1]) + int(res[1] == input_tuple[2])
    time_score = int(res[2] == input_tuple[3]) + int(res[3] == input_tuple[4])
    title_score = int(res[4] == input_tuple[5])
    location_score = int(res[5] == input_tuple[6])
    full_score = int((date_score + time_score + title_score + location_score) == 6)

    BOLD = '\033[1m'
    END = '\033[0m'

    if (full_score != 1):
        s = raw 
        for i in range(6):
            if res[i] != input_tuple[i+1]:
                s += f"|\033[1m{res[i]}\033[0m"
            else:
                s += f"|ok"
        print(s)

    return (date_score, time_score, title_score, location_score, full_score)


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
        if res[4] == 1: full_success += 1

    print(f"Correctly parsed date: {date_success} time: {time_success} "
          f"title: {title_success} loc: {location_success} "
          f"full: {full_success} of {len(testdata)}")
       
run()


