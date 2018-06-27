#

import nltk
import re
import sys
from datetime import *
from dateutil import relativedelta
from etoken import *
from spelled_numbers import handle_spelled_number
from testdata import testdata

meridian_txt= ["a", "am", "a.m.", "p", "pm", "p.m."]
day_txt = ["day", "days", "d"]
week_txt = ["week", "weeks", "wk"]
month_txt = ["month", "months", "mon"]

weekday_to_num = {"monday": 0, "mon": 0, "mo": 0,
                  "tuesday": 1, "tue": 1, "tues": 1, "tu": 1,
                  "wednesday": 2, "wed": 2, "weds": 2,
                  "thursday": 3, "thu": 3, "thur": 3, "thurs": 3, "th": 3,
                  "friday": 4, "fri": 4, "fr": 4,
                  "saturday": 5, "sat": 5,
                  "sunday": 6, "sun": 6 }

month_to_num = {"january": 1, "jan": 1, "february": 2, "feb": 2,
                "march": 3, "mar": 3, "april": 4, "apr": 4, "may": 5,
                "june": 6, "jun": 6, "july": 7, "jul": 7,
                "august": 8, "aug": 8, "september": 9, "sept": 9, "sep": 9,
                "october": 10, "oct": 10, "november": 11, "nov": 11,
                "december": 12, "dec": 12 }

today = date.today()
tomorrow = today + timedelta(days=1)
yesterday = today - timedelta(days=1)

# if 4-digit years are specified, they must fall in this range
year_range = [1900, 2099]


def is_token_time(tok: EToken) -> bool:
    """Determine whether tok is a time, looking just at the token itself."""

    # is it a special string?
    spec = ["noon", "midnight", "sunrise", "sunset", "oclock", "o'clock"]
    if tok.val in spec:
        return True

    return False


def is_token_date(tok: EToken) -> bool:
    """Determine whether tok is a date, looking just at the token itself."""

    # is it a day of the week?
    if tok.val in weekday_to_num:
        return True

    # is it a month name?
    if tok.val in month_to_num:
        return True

    # is it a special string?
    if tok.val in ["today", "tomorrow", "yesterday"]:
        return True

    return False


def remove_poss(tagged):
    """Concatenate any possessives with the preceding item"""
    ret = []
    last = None
    for t in tagged:
        if t[1] == "POS":
            last = (last[0] + t[0], last[1])
        else:
            if last is not None:
                ret.append(last)
            last = t
    if last is not None:
        ret.append(last)
    return ret


def parse_for_time_date_range(tok: EToken, lookahead: EToken) -> list:
    """If this single token appears to be of the form (time)-(time) or
    (date)-(date), return three tokens: "start" "to" "end"; else
    just return a one-item list containing the token.
    """

    # time
    ampm       =  r"(?:(?:[ap]m?)|(?:[ap]\.?m\.?))"  # a, am, a.m.
    timespec   = r"\d{1,2}:\d{2}(?::\d{2})?" + ampm + "?" # hh:mm[:ss][am]
    hourspec_m = r"\d{1,2}" + ampm   # hh[am] - am/pm present
    hourspec   = hourspec_m + "?"    # hh[am] - am/pm optional

    m = re.match(f"^({timespec})-({timespec})$", tok.val)
    if m:
        start = EToken(m.group(1), "CD", "ST_TIME")
        to = EToken("to", ":", "IGN")
        end = EToken(m.group(2), "CD", "END_TIME")
        return [start, to, end]

    m = re.match(f"^({timespec})-({hourspec})$", tok.val)
    if m:
        start = EToken(m.group(1), "CD", "ST_TIME")
        to = EToken("to", ":", "IGN")
        end = EToken(m.group(2), "CD", "END_TIME")
        return [start, to, end]

    m = re.match(f"^({hourspec})-({timespec})$", tok.val)
    if m:
        start = EToken(m.group(1), "CD", "ST_TIME")
        to = EToken("to", ":", "IGN")
        end = EToken(m.group(2), "CD", "END_TIME")
        return [start, to, end]

    m = re.match(f"^({hourspec_m})-({hourspec})$", tok.val)
    if m:
        start = EToken(m.group(1), "CD", "ST_TIME")
        to = EToken("to", ":", "IGN")
        end = EToken(m.group(2), "CD", "END_TIME")
        return [start, to, end]

    m = re.match(f"^({hourspec})-({hourspec_m})$", tok.val)
    if m:
        start = EToken(m.group(1), "CD", "ST_TIME")
        to = EToken("to", ":", "IGN")
        end = EToken(m.group(2), "CD", "END_TIME")
        return [start, to, end]

    if (lookahead.match(meridian_txt)):
        m = re.match(f"^({hourspec})-({hourspec})$", tok.val)
        if m:
            start = EToken(m.group(1), "CD", "ST_TIME")
            to = EToken("to", ":", "IGN")
            end = EToken(m.group(2), "CD", "END_TIME")
            return [start, to, end]

    m = re.match(f"^{timespec}$", tok.val)
    if m:
        tok.sem = "TIME"
        return [tok]

    m = re.match(f"^{hourspec_m}$", tok.val)
    if m:
        tok.sem = "TIME"
        return [tok]

    # hho'clock -- fix up val in this case
    m = re.match(r"^(\d{1,2})o'?clock", tok.val)
    if m:
        tok.val = f"{m.group(1)}:00"
        tok.sem = "TIME"
        return [tok]

    ## hh o'clock
    if (lookahead.match(["o'clock", "oclock"])):
        m = re.match(r"^(\d{1,2})$", tok.val)
        if m:
            tok.val = f"{m.group(1)}:00"
            tok.sem = "TIME"
            return [tok]

    # date
    datespec = r"\d{1,2}/\d{1,2}(?:/(?:\d{2}|\d{4}))?" # mm/dd/yy or mm/dd/yyyy
    datespec_yfirst = r"\d{4}/\d{1,2}/\d{1,2}" # yyyy/mm/dd
    m = re.match(f"^({datespec})-({datespec})$", tok.val)
    if m:
        start = EToken(m.group(1), "CD", "ST_DATE")
        to = EToken("to", ":", "IGN")
        end = EToken(m.group(2), "CD", "END_DATE")
        return [start, to, end]

    m = re.match(f"^({datespec_yfirst})-({datespec_yfirst})$", tok.val)
    if m:
        start = EToken(m.group(1), "CD", "ST_DATE")
        to = EToken("to", ":", "IGN")
        end = EToken(m.group(2), "CD", "END_DATE")
        return [start, to, end]

    m = re.match(f"^{datespec}$", tok.val)
    if m:
        tok.sem = "DATE"
        return [tok]

    m = re.match(f"^{datespec_yfirst}$", tok.val)
    if m:
        tok.sem = "DATE"
        return [tok]

    # we have to be conservative with dates specified using
    # hyphens. For now, if it is dd-mm-yyyy or dd-mm-yy, and the xx
    # values are all in the range 1-31, and the year, if 4 digits, is
    # between [-50,+49] years from now, then assume single date; in
    # this case, fixup tok.val to use the slash form of the date
    m = re.match(r"^(\d{1,2})-(\d{1,2})-(\d{2}|\d{4})$", tok.val)
    if m:
        month = int(m.group(1))
        day = int(m.group(2))
        year = int(m.group(3))
        if (1 <= month <= 12 and 1 <= day <= 31):
            if year < 100:
                year += 2000
                if year > today.year + 49:
                    year -= 100
            if (today.year-50 <= year <= today.year+49):
                tok.val = f"{month}/{day}/{year}"
                tok.sem = "DATE"
                return [tok]

    # same as above, for the form yyyy-xx-xx
    m = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})$", tok.val)
    if m:
        year = int(m.group(1))
        month = int(m.group(2))
        day  = int(m.group(3))
        if (1 <= day <= 31 and 1 <= month <= 12):
            if year < 100:
                year += 2000
                if year > today.year + 49:
                    year -= 100
            if (today.year-50 <= year <= today.year+49):
                tok.val = f"{month}/{day}/{year}"
                tok.sem = "DATE"
                return [tok]


    return [tok]


def parse_time(s: str) -> time:
    """Attempt to parse a string into a time.

    If the input string is a time in one of the forms:
        hh:mm[:ss]am (where seconds and am/pm can be omitted)
        hham (where am/pm can be omitted)
        xxxx (military time, 3 or 4 digits)
    or if it is one of the special strings "midnight" or "noon"

    return the corresponding datetime.time object, otherwise return None.
    """

    # special cases
    if s == "midnight":
        return time(0)
    if s == "noon":
        return time(12)

    hour = None
    minutes = None
    seconds = 0

    is_pm = False
    meridian_specified = False

    # TODO: there's a quite a bit of overlap between this function and
    # parse_for_time_date_range -- would like to collapse these into
    # one
    ampm     = r"((?:[ap]m?)|(?:[ap]\.?m\.?))?"  # a, am, a.m.
    timespec = r"^(\d{1,2}):(\d{2})(:\d{2})?" + ampm + "$" # hh:mm[:ss][am]
    hourspec = r"^(\d{1,2})" + ampm + "$"    # hh[am]
    milspec  = r"^(\d{1,2})(\d{2})" + ampm + "$"    # hhmm[am], 1 or 2 h digits

    m = re.match(timespec, s)
    if m:
        hour = int(m.group(1))
        minutes = int(m.group(2))
        if (m.group(3)):
            seconds = int(m.group(3)[1:])
        if m.group(4):
            meridian_specified = True
            if m.group(4).lower() in ["pm", "p", "p.m."]:
                is_pm = True

    if not hour:
        m = re.match(hourspec, s)
        if m:
            hour = int(m.group(1))
            minutes = 0

            if m.group(2):
                meridian_specified = True
                if m.group(2).lower() in ["pm", "p", "p.m."]:
                    is_pm = True

    if not hour:
        m = re.match(milspec, s)
        if m:
            hour = int(m.group(1))
            minutes = int(m.group(2))
            if m.group(3):
                meridian_specified = True
                if m.group(3).lower() in ["pm", "p", "p.m."]:
                    is_pm = True
            else:
                # if 4 digits specified, then force am/pm. "0600" == 6 am
                if (len(m.group(1)) == 2):
                    meridian_specified = True
                    is_pm = (hour == 12)

    if not hour:
        return None
    
    if (hour < 0 or hour > 23):
        return None
    if (minutes < 0 or minutes > 59):
        return None
    if (seconds < 0 or seconds > 59):
        return None

    if (not meridian_specified and hour <= 6):
        is_pm = True

    if (not is_pm and hour == 12):
        hour = 0    # midnight

    if is_pm and hour < 12:
        hour += 12

    return time(hour=hour, minute=minutes, second=seconds)


def year_from_month_and_day(month: int, day:int) -> int:
    """Return the year for the next occurrence of (month, day).

    The returned year might be this year, or next year, depending on
    whether (month, day) has already happened this year. (If (month,
    day) describes today, return today.)
    """
    trial_date = date(today.year, month, day)
    if (trial_date < today):
        return today.year + 1
    return today.year


def date_from_day(day_num: int) -> date:
    """When someone says "meet on the 3rd", returns the next such day"""
    if today.day < day_num:
        return today.replace(day=day_num)
    # it's next month
    if today.month == 12: return date(today.year + 1, 1, day_num)
    return date(today.year, today.month+1, day_num)


def date_from_month_day(month: int, day: int) -> date:
    """When someone says "meet on the 3rd", returns the next such day"""
    if today.day < day_num:
        return today.replace(day=day_num)
    # it's next month
    if today.month == 12: return date(today.year + 1, 1, day_num)
    return date(today.year, today.month+1, day_num)


def parse_date(s: str) -> date:
    """Attempt to parse a string into a datetime.date.

    Handles the following cases:
        yyyy/mm/dd or yyyy-mm-dd (year must be 4 digits)
        mm/dd/yyyy or mm-dd-yyyy (where year can be omitted, or 2 or 4 digits)
        a weekday - returns the next such day after today
        today
        tomorrow
        yesterday
    """

    # first parse weekdays
    if s in weekday_to_num:
        wd = weekday_to_num[s]
        td = today.weekday()
        delta = wd - td
        if delta <= 0:
            delta += 7
        return today + timedelta(delta)

    # today, tomorrow
    if s == "today": return today
    if s == "tomorrow": return tomorrow
    if s == "yesterday": return yesterday

    year = None
    month = None
    day = None

    # match date: yyyy/mm/dd. must be 4 digit yr and year must be specified
    m = re.match(r"^(\d{4})(?P<sep>[-/])(\d{1,2})(?P=sep)(\d{1,2})$", s)
    if m :
        year = int(m.group(1))
        month = int(m.group(3))
        day = int(m.group(4))

    # match date: mm/dd/yyyy or mm/dd/yy, year may be omitted
    m = re.match(r"^(\d{1,2})(?P<sep>[-/])(\d{1,2})((?P=sep)(?:\d{2}|\d{4}))?$", s)
    if m :
        month = int(m.group(1))
        day = int(m.group(3))
        if (m.group(4)):
            year=int(m.group(4)[1:])
            # arbitrarily: 2-digit years interpreted as within [-50,+49] of today
            if year < 100:
                year += 2000
                if year > today.year + 49:
                    year -= 100
        else:
            year = year_from_month_and_day(month, day)

    if (year is None or month is None or day is None or
        (not min(year_range) <= year <= max(year_range)) or
        (not 1 <= month <= 12) or day < 1):
        return None

    try:
        return date(year=year, month=month, day=day)
    except ValueError:
        # this happens if day is higher than allowed for month
        return None


def parse_possible_spelled_date(t_mon: EToken,
                                t_day: EToken,
                                t_year: EToken) -> bool:
    """If possible, parse the three tokens into a datetime.date.

    We have a possible date, with 2 or 3 tokens:
       t_mon - a spelled out month
       t_day - a day, either CD or OD form
       t_year - either None, or a possible year in CD form

    If possible, parse this into a datetime.date, and update the
    tokens. The datetime.date object will be hung on the t_day token,
    and the t_mon (and t_year, if used) tokens will be set to IGN.

    Return True if parsable, False otherwise.
    """

    try:
        month = month_to_num[t_mon.val]
        day = int(t_day.val)
        year = None
        if t_year and t_year.sem not in (EToken.time_sems + EToken.date_sems):
            m = re.match(r"^\d{4}$", t_year.val)
            if m:
                if min(year_range) <= int(m.group(0)) <= max(year_range):
                    year = int(m.group(0))
                    t_year.sem = "IGN"
        if not year:
            year = year_from_month_and_day(month, day)
        t_day.date = date(year, month, day)
        t_day.val = f"{year}/{month}/{day}"
        if t_day.sem == "-": t_day.sem = "DATE"
        t_mon.sem = "IGN"
        return True
    except:
        return False


def parse_phrase(tok_list: list): 
    """Parse for multi-word phrases.

    When called, examine the provided string of tokens. The list is
    guaranteed to have one element -- e.g., t[0] is guaranteed to
    exist. Other tokens might not be present.
    """

    t = padded(tok_list, 10)

    # (from - optional) (month) (OD or CD) (to | until | til) (OD or CD)
    #       (comma - opt) (CD - opt year)
    # TODO: add until/til
    m = 0
    if t[0].match("from", "IN"):
        m += 1
    if (t[m].match(month_to_num) and t[m+1].match(pos=["OD","CD"])
        and t[m+2].match("to","TO") and t[m+3].match(pos=["OD","CD"])):
        t[0].sem = "IGN"
        y = m+4
        if t[y].match(",", pos=","): y += 1
        if t[y].match(pos="CD"):
            year_tok = t[y]
        else:
            year_tok = None
        res = parse_possible_spelled_date(t[m], t[m+1], t[y])
        if res:
            res = parse_possible_spelled_date(t[m], t[m+3], t[y])
        if res:
            t[m+1].sem = "ST_DATE"
            t[m+3].sem = "END_DATE"
            return
    
    # (at) (time or CD)
    if (t[0].match("at", "IN") and 
        (t[1].match(sem=EToken.time_sems) or t[1].match(sem="-", pos="CD"))):
        t[0].sem = "IGN"
        t[1].time = parse_time(t[1].val)
        if not t[1].match(sem=EToken.time_sems): t[1].sem = "TIME"
        return

    # TODO: add optional from
    # (date) (to or until or til) (date)
    if (t[0].match(sem=EToken.date_sems) and t[1].sem != "IGN" and
        (t[1].match("to", "TO") or t[1].match("until", "IN") or t[1].match("til")) 
        and t[2].match(sem=EToken.date_sems)):
        t[0].date = parse_date(t[0].val)
        t[0].sem = "ST_DATE"
        t[1].sem = "IGN"
        t[2].date = parse_date(t[2].val)
        t[2].sem = "END_DATE"
        return
    
    # TODO: add optional from
    # (time or CD) (to or until or til) (time or CD)
    if ((t[0].match(sem=EToken.time_sems) or t[0].match(sem="-", pos="CD")) and
        t[1].sem != "IGN" and
        (t[1].match("to", "TO") or t[1].match("until", "IN") or t[1].match("til")) 
        and (t[2].match(sem=EToken.time_sems) or t[2].match(sem="-", pos="CD"))):
        t[0].time = parse_time(t[0].val)
        t[0].sem = "ST_TIME"
        t[1].sem = "IGN"
        t[2].time = parse_time(t[2].val)
        t[2].sem = "END_TIME"
        return

    # (on) (date)
    if (t[0].match("on", "IN") and t[1].match(sem=EToken.date_sems)):
        t[0].sem = "IGN"
        t[1].date = parse_date(t[1].val)
        return

    # (the) (OD)  (for instance, "the 21st" - assume next such day)
    if (t[0].match("the", "DT") and t[1].match(pos="OD")):
        t[0].sem = "IGN"
        t[1].date = date_from_day(int(t[1].val))
        t[1].sem = "DATE"
        return

    # (month) (comma or THE - optional) (OD or CD) (comma - optional) (CD - optional - year)
    d = 1
    if (t[d].match(",", pos=",") or t[d].match("the", "DT")): d += 1
    if (t[0].match(month_to_num) and t[d].match(pos=["CD", "OD"])):
        y = d+1
        if t[y].match(",", pos=","): y += 1
        if t[y].match(pos="CD"):
            res = parse_possible_spelled_date(t[0], t[d], t[y])
        else:
            res = parse_possible_spelled_date(t[0], t[d], None)
        if res: return

    # (OD or CD) (comma or OF - optional) (month) (comma - optional) (CD - optional - year)
    m = 1
    if (t[m].match(",", pos=",") or t[m].match("of", pos="IN")): m += 1
    if (t[0].match(pos=["CD", "OD"]) and t[m].match(month_to_num)):
        y = m+1
        if t[y].match(",", pos=","): y += 1
        if t[y].match(pos="CD"):
            res = parse_possible_spelled_date(t[m], t[0], t[y])
        else:
            res = parse_possible_spelled_date(t[m], t[0], None)
        if res: return

    # (in - optional) ("a" or CD) (week | month | day)  (from (date) - optional)
    if ((t[0].match("a", pos="DT") or t[0].match(pos="CD")) and
        t[1].match(week_txt + month_txt + day_txt)):
        if t[0].val == "a":
            num = 1
        else:
            num = int(t[0].val)
        anchor = today
        if (t[2].match("from", "IN") and t[3].match(sem=EToken.date_sems)
            and parse_date(t[3].val)):
            anchor =  parse_date(t[3].val)
            t[2].sem = "IGN"
            t[3].sem = "IGN"
        if (t[1].match(week_txt)):
            t[0].date = anchor + timedelta(weeks=num)
        elif (t[1].match(month_txt)):
            t[0].date = anchor + relativedelta.relativedelta(months=num)
        else:   # days
            t[0].date = anchor + timedelta(days=num)
        t[0].sem = "DATE"
        t[1].sem = "IGN"
        return


    # TODO!
    
    # in dd (minutes | hours | days)


def parse(raw, debug = False):
    """Parse the raw string. 

    Returns tuple (start date, end date, start time, end time, title, location)
    """

    tokenized = nltk.word_tokenize(raw)
    tagged = remove_poss(nltk.pos_tag(tokenized))

    token_list = []
    for t in tagged:
        token_list.append(EToken(*t))

    ol = []
    for (tok, lookahead) in zip(token_list, token_list[1:] + [ETokenNull()]):
        ol.extend(parse_for_time_date_range(tok, lookahead))
    token_list = ol

    if (debug):
        print(f"After tokenization: {token_list}")

    # First pass: parse items that can be determined just by looking
    # at a single token by itself
    for t in token_list:
        if t.val == "-" and t.pos == ":":
            t.val = "to"
            t.pos = "TO"
        handle_spelled_number(t)
        if is_token_time(t):
            t.sem = "TIME"
        elif is_token_date(t):
            t.sem = "DATE"

    # second pass: if there are any TIME or CD's, followed by am/pm,
    # collapse these into a single token
    #
    # TODO: There must be a more pythonic way to iterate over this list
    ol = []
    ll = len(token_list)
    i = 0
    while (i < ll):
        tok = token_list[i]
        if (tok and (tok.match(sem=EToken.time_sems) or tok.match(pos="CD"))
            and i+1 < ll and token_list[i+1].match(val=meridian_txt)):
            tok.val += token_list[i+1].val
            if tok.sem == "-":
                tok.sem = "TIME"
            i += 2
        else:
            i += 1
        ol.append(tok)
    token_list = ol

    if (debug):
        print(f"Before parsing for phrases: {token_list}")

    # Second pass: parse for phrases
    for i in range(len(token_list)):
        parse_phrase(token_list[i:])

    if (debug):
        print(f"after phrase parsing: {token_list}")

    # Third pass: find any times/dates not yet parsed
    for t in token_list:
        if t.match(sem=EToken.time_sems) and t.time is None:
            t.time = parse_time(t.val)
        elif t.match(sem=EToken.date_sems) and t.date is None:
            t.date = parse_date(t.val)

    if (debug):
        print(f"After all parsing: {token_list}")

    # now see if we have any dates/times. first, look for explicit
    # st_time or st_date

    st_time = None
    end_time = None
    st_date = None
    end_date = None

    for t in token_list:
        if t.sem == "ST_TIME" and t.time is not None:
            assert(st_time is None)
            st_time = t.time
        elif t.sem == "END_TIME" and t.time is not None:
            assert(end_time is None)
            end_time = t.time
        elif t.sem == "ST_DATE" and t.date is not None:
            assert(st_date is None)
            st_date = t.date
        elif t.sem == "END_DATE" and t.date is not None:
            assert(end_date is None)
            end_date = t.date

    # now if no st_time and there's just a TIME, make that st_time,
    # likewise for dates
    for t in token_list:
        if t.sem == "TIME" and t.time is not None:
            if st_time is None:
                st_time = t.time
            elif end_time is None:
                end_time = t.time
        if t.sem == "DATE" and t.date is not None:
            if st_date is None:
                st_date = t.date
            elif end_date is None:
                end_date = t.date


    # location and title are the concatenation of the corresponding
    # tokens
    location = ""
    title = ""
    for t in token_list:
        if t.sem == "LOCATION":
            location += t.orig + " "
        if t.sem == "TITLE":
            title += t.orig + " "

    if location == "":
        location = None
    if title == "":
        title = None

    ret = (st_date, end_date, st_time, end_time, title, location)

    if (debug):
        print(f"Returning: {ret}")

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
    metadata_score = int(res[4] == input_tuple[5]) + int(res[5] == input_tuple[6])

    if (date_score != 2 or time_score != 2):
        print(f"{raw}, {res}")

    return (date_score, time_score, metadata_score)


def run():
    date_success = 0
    time_success = 0
    metadata_success = 0
    for t in testdata:
        res = test_parse(t)
        if res[0] == 2: date_success += 1
        if res[1] == 2: time_success += 1
        if res[2] == 2: metadata_success += 1

    print(f"Correctly parsed (date: {date_success}, time: {time_success}, "
          f"md: {metadata_success}) of {len(testdata)}")
        
run()

