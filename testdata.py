# testdata.py: test data for parsing by calendar natural language
# processor.
#
# Some test cases based on cases from
#     https://github.com/jeffreyrosenbluth/CalNLP
#
# The remainder copyright (C) 2018 Cardinal Peak LLC
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


from datetime import date, time, timedelta, datetime
from dateutil import relativedelta
today = date.today()
tomorrow = date.today() + timedelta(days=1)
yesterday = date.today() - timedelta(days=1)

def weekday_to_num(s: str) -> int:
    """Given a weekday, return the corresponding day-of-week.

    Specifically:
       Monday    -> 0
       Tuesday   -> 1
       Wednesday -> 2
       Thursday  -> 3
       Friday    -> 4
       Saturday  -> 5
       Sunday    -> 6
    """
    day_list = ["monday", "tuesday", "wednesday", "thursday", "friday",
                "saturday", "sunday"]
    return day_list.index(s.lower())

def map_day(rel_day: str) -> date:
    """Map a relative string description into an absolute date.

    Handles the following relative dates:

    - For a day-of-the-week string (e.g., "Monday"), returns the date
      object corresponding to the next such day. This will be between
      1 and 7 days in the future, so for instance if today is a
      Wednesday and "Wednesday" is passed in, returns the date
      corresponding to one week from today.

    - For the word "last" followed by a day-of-the-week string (e.g.,
      "last Tuesday"), returns the date object corresponding to
      between 1 and 7 days ago.
    """
    rel_day = rel_day.lower()

    td = today.weekday()

    if rel_day.startswith("last "):
        wd = weekday_to_num(rel_day[5:])
        delta = td - wd
        if delta <= 0:
            delta += 7
        return today - timedelta(days=delta)

    wd = weekday_to_num(rel_day)
    delta = wd - td
    if delta <= 0:
        delta += 7
    return today + timedelta(days=delta)
    
def next_monthday(day_num: int) -> date:
    """When someone says "meet on the 3rd", returns the next such day"""
    if today.day < day_num:
        return today.replace(day=day_num)
    # it's next month
    if today.month == 12: return date(today.year + 1, 1, day_num)
    return date(today.year, today.month+1, day_num)

def next_day(mon: int, day:int) -> date:
    """Given the month and day, return the next such date, which might be next
    year."""
    trial_date = date(today.year, mon, day)
    if (trial_date < today):
        return(date(today.year + 1, mon, day))
    return trial_date

def in_x_min(minutes: int) -> time:
    """Return a time that is the specified minutes in the future"""
    now = datetime.now()
    tm = (now + timedelta(minutes=minutes)).time()
    return tm.replace(second=0, microsecond=0)
    
def in_x_months(mons: int, anchor: date = today) -> date:
    """Return the date that is the specified number of months in the
    future from the anchor date (default: today).
    """
    return anchor + relativedelta.relativedelta(months=mons)


# From here down is a list of test data. Each item is a tuple with the
# following values:

#   the test string
#   start day, as a date object, or None
#   end day, as a date object, or None
#   start time, as a time object, or None
#   end time, as a time object, or None
#   event name
#   event location
    
# If there is only one date, it is assumed to be both the start and
# end date.  If no end time is specified, the end_time value will be None.

# not yet included:
#    time zones (such as "at 5 pm EST")
#    recurring events

testdata = [
    ("Friday breakfast at 8 at Lucky's",
     map_day("Friday"), map_day("Friday"), time(8), None, "breakfast",
     "Lucky's"),

    ("Thursday 7 am Ride with Arn at Amante",
     map_day("Thursday"), map_day("Thursday"), time(7), None, "Ride with Arn",
     "Amante"),

    ("Meet Bill at Starbucks next Tuesday from 11 to noon",
     map_day("Tuesday"), map_day("Tuesday"), time(11), time(12), "Meet Bill",
     "Starbucks"),

    ("Let's meet at Twisted Pine at 5 pm to catch up",
     None, None, time(17), None, "Let's meet to catch up", "Twisted Pine"),

    ("Let's grab coffee at 9:30 am on Wednesday",
     map_day("Wednesday"), map_day("Wednesday"), time(9, 30), None,
     "Let's grab coffee", None),

    ("Run today at 1:30",
     today, today, time(13, 30), None, "Run", None),

    ("Dave and I have a meeting to go down to the AF Academy on July 12th",
     next_day(7, 12), next_day(7, 12), None, None,
     "Dave and I have a meeting to go down", "AF Academy"),

    ("Cycling with Arn and Karen on Thursday at 7:15 AM at Amante",
     map_day("Thursday"), map_day("Thursday"), time(7,15), None,
     "Cycling with Arn and Karen", "Amante"),

    ("Meet at your house at 6 am",
     None, None, time(6), None, "Meet", "your house"),

    ("Meet thurs 8-10 am",
     map_day("Thursday"), map_day("Thursday"), time(8), time(10), "Meet",
     None),

    ("DL 1257 Jun 21 2019 6am - 7am",
     date(2019, 6, 21), date(2019, 6, 21), time(6), time(7), "DL 1257", None),

    ("DL 1257 Jun 21 6am - 7am",
     next_day(6, 21), next_day(6, 21), time(6), time(7), "DL 1257", None),

    ("Saturday 6 pm to 8 pm Oceans 8 at Cinemark ",
     map_day("Saturday"), map_day("Saturday"), time(18), time(20), "Oceans 8",
     "Cinemark"),

    ("Saturday, 6 pm to 8 pm Oceans 8 at Cinemark ",
     map_day("Saturday"), map_day("Saturday"), time(18), time(20), "Oceans 8",
     "Cinemark"),

    ("Sunday 9:30 to noon Genny ride at Rayback Collective",
     map_day("Sunday"), map_day("Sunday"), time(9,30), time(12), "Genny ride",
     "Rayback Collective"),

    ("Grocery shopping at King Kullen Thursday at 11:30pm",
     map_day("Thursday"), map_day("Thursday"), time(23, 30), None,
     "Grocery shopping", "King Kullen"),

    ("Grocery shopping at Waldbaums from 4pm to 5pm", 
     None, None, time(16), time(17), "Grocery shopping",
     "Waldbaums"),

    ("Meet at Room 321 Thursday at 10:00 am",
     map_day("Thursday"), map_day("Thursday"), time(10), None, "Meet",
     "Room 321"),

    ("Meet at Room 321 Thursday at 10 am",
     map_day("Thursday"), map_day("Thursday"), time(10), None, "Meet",
     "Room 321"),

    ("Meet at Room 321 Thursday at 10",
     map_day("Thursday"), map_day("Thursday"), time(10), None, "Meet",
     "Room 321"),

    ("Meet at Room 321 Thursday at 10 o'clock",
     map_day("Thursday"), map_day("Thursday"), time(10), None, "Meet",
     "Room 321"),
     
    ("Meet at Room 321 Thursday at 10o'clock",
     map_day("Thursday"), map_day("Thursday"), time(10), None, "Meet",
     "Room 321"),
     
    ("Meet at Room Three Thursday at ten",
     map_day("Thursday"), map_day("Thursday"), time(10), None, "Meet",
     "Room Three"),

    ("Clothes shopping Wednesday at 5:35pm at Nordstroms", 
     map_day("Wednesday"), map_day("Wednesday"), time(17, 35), None,
     "Clothes shopping", "Nordstroms"),

    ("Clothes shopping at Nordstroms next Thursday at 5p", 
     map_day("Thursday"), map_day("Thursday"), time(17), None,
     "Clothes shopping", "Nordstroms"),

    ("Clothes shopping at Nordstroms tomorrow at 0600", 
     tomorrow, tomorrow, time(6), None, "Clothes shopping",
     "Nordstroms"),

    ("Clothes shopping at Nordstroms tomorrow at 1200", 
     tomorrow, tomorrow, time(12), None, "Clothes shopping",
     "Nordstroms"),

    ("Clothes shopping at Nordstroms thursday to saturday", 
     map_day("Thursday"), map_day("Thursday") + timedelta(days=2), None, None,
     "Clothes shopping", "Nordstroms"),

    ("Clothes shopping at Nordstroms 23 sep at 2:00", 
     next_day(9, 23), next_day(9, 23), time(14), None, "Clothes shopping",
     "Nordstroms"),

    ("Clothes shopping at Nordstroms 23 Apr at 2", 
     next_day(4, 23), next_day(4, 23), time(14), None, "Clothes shopping",
     "Nordstroms"),

    ("Clothes shopping at Nordstroms 23 sep at noon", 
     next_day(9, 23), next_day(9, 23), time(12), None, "Clothes shopping",
     "Nordstroms"),

    ("Clothes shopping at Nordstroms 23 sep at midnight", 
     next_day(9, 23), next_day(9, 23), time(0), None, "Clothes shopping",
     "Nordstroms"),

    ("Family vacation from 8/9 - 8/18", 
     next_day(8, 9), next_day(8, 9) + timedelta(days=9), None, None,
     "Family vacation", None),

    ("Family vacation from 8/1 to 8/8 at The Sandy Lane", 
     next_day(8, 1), next_day(8, 1) + timedelta(days=7), None, None,
     "Family vacation", "The Sandy Lane"),

    ("Family vacation from August 9th - 18th in Mexico", 
     next_day(8, 9), next_day(8, 9) + timedelta(days=9), None, None,
     "Family vacation", "Mexico"),

    ("Family vacation from August 9th - 18 in Mexico", 
     next_day(8, 9), next_day(8, 9) + timedelta(days=9), None, None,
     "Family vacation", "Mexico"),

    ("Family vacation from August 9 - 18 at The Marriott Hotel", 
     next_day(8, 9), next_day(8, 9) + timedelta(days=9), None, None,
     "Family vacation", "The Marriott Hotel"),

    ("Soccer practice next Wednesday at 6am at JFK High School", 
     map_day("Wednesday"), map_day("Wednesday"), time(6), None,
     "Soccer practice", "JFK High School"),

    ("Soccer practice tomorrow at 6 at JFK High School", 
     tomorrow, tomorrow, time(6), None, "Soccer practice",
     "JFK High School"),

    ("Sam's birthday on 5/16", 
     next_day(5, 16), next_day(5, 16), None, None, "Sam's birthday", None),

    ("Meet at Howdy's office Thursday at 5:00 am",
     map_day("Thursday"), map_day("Thursday"), time(5), None, "Meet",
     "Howdy's office"),

    ("Bike ride 6/20 at 5am",
     next_day(6, 20), next_day(6, 20), time(5), None, "Bike ride", None),

    ("Bike ride 6/20/18 at 5am",
     date(2018, 6, 20), date(2018, 6, 20), time(5), None, "Bike ride", None),

    ("Bike ride 6/20/2018 at 5am",
     date(2018, 6, 20), date(2018, 6, 20), time(5), None, "Bike ride", None),

    ("Bike ride 6-20 at 5am",
     next_day(6, 20), next_day(6, 20), time(5), None, "Bike ride", None),

    ("Bike ride 6-20-18 at 5am",
     date(2018, 6, 20), date(2018, 6, 20), time(5), None, "Bike ride", None),

    ("Bike ride 6-20-2018 at noon",
     date(2018, 6, 20), date(2018, 6, 20), time(12), None, "Bike ride", None),

    ("Lunch with John in Cupertino on Thursday from 11-1:30pm", 
     map_day("Thursday"), map_day("Thursday"), time(11), time(13, 30),
     "Lunch with John", "Cupertino"),

    ("Lunch with John in Cupertino on Thursday from 11-1:30 pm", 
     map_day("Thursday"), map_day("Thursday"), time(11), time(13, 30),
     "Lunch with John", "Cupertino"),

    ("Lunch with John in Cupertino on Friday @12", 
     map_day("Friday"), map_day("Friday"), time(12), None, "Lunch with John",
     "Cupertino"),

    ("Lunch with John in Cupertino on Thursday from 11-1:30",
     map_day("Thursday"), map_day("Thursday"), time(11), time(13,30),
     "Lunch with John", "Cupertino"),

    ("Lunch with John Carlucci in Cupertino on Thursday from 11-1:30pm",
     map_day("Thursday"), map_day("Thursday"), time(11), time(13,30),
     "Lunch with John Carlucci", "Cupertino"),

    ("Lunch with John in Cupertino on Thursday from 11-1:00",
     map_day("Thursday"), map_day("Thursday"), time(11), time(13),
     "Lunch with John", "Cupertino"),

    ("Lunch with John in Cupertino on Thursday from 11-1:00pm",
     map_day("Thursday"), map_day("Thursday"), time(11), time(13),
     "Lunch with John", "Cupertino"),

    ("Lunch with John in Cupertino on Thursday from 11-1",
     map_day("Thursday"), map_day("Thursday"), time(11), time(13),
     "Lunch with John", "Cupertino"),

    ("Lunch with John in Cupertino on Thursday from 11-1p",
     map_day("Thursday"), map_day("Thursday"), time(11), time(13),
     "Lunch with John", "Cupertino"),

    ("Lunch with John in Cupertino on Thursday from 11-1pm",
     map_day("Thursday"), map_day("Thursday"), time(11), time(13),
     "Lunch with John", "Cupertino"),

    ("Lunch with John in Cupertino on Thursday from 11-1A",
     map_day("Thursday"), map_day("Thursday"), time(11), time(13),
     "Lunch with John", "Cupertino"),

    ("Lunch with John in Cupertino on Thursday From 11-1am",
     map_day("Thursday"), map_day("Thursday"), time(11), time(13),
     "Lunch with John", "Cupertino"),

    ("Lunch with John in Cupertino on Thursday from 11:15-1:30",
     map_day("Thursday"), map_day("Thursday"), time(11,15), time(13,30),
     "Lunch with John", "Cupertino"),

    ("Lunch with John in Cupertino on Thursday from 11:15-1:30pm",
     map_day("Thursday"), map_day("Thursday"), time(11,15), time(13,30),
     "Lunch with John", "Cupertino"),

    ("Lunch with John in Cupertino on Thursday from 11:15-1:00",
     map_day("Thursday"), map_day("Thursday"), time(11,15), time(13),
     "Lunch with John", "Cupertino"),
    
    ("Lunch with John in Cupertino on Thursday from 11:15-1:00pm",
     map_day("Thursday"), map_day("Thursday"), time(11,15), time(13),
     "Lunch with John", "Cupertino"),
    
    ("Lunch with John in Cupertino on Thursday from 11:15-1",
     map_day("Thursday"), map_day("Thursday"), time(11, 15), time(13),
     "Lunch with John", "Cupertino"),
    
    ("Lunch with John in Cupertino on Thursday from 11:15-1p",
     map_day("Thursday"), map_day("Thursday"), time(11, 15), time(13),
     "Lunch with John", "Cupertino"),
    
    ("Lunch with John in Cupertino on Thursday from 11:15-1pm",
     map_day("Thursday"), map_day("Thursday"), time(11, 15), time(13),
     "Lunch with John", "Cupertino"),
    
    ("Lunch with John in Cupertino on Thursday from 11:15-1A",
     map_day("Thursday"), map_day("Thursday"), time(11, 15), time(1),
     "Lunch with John", "Cupertino"),
    
    ("Lunch with John in Cupertino on Thursday From 11:15-1am",
     map_day("Thursday"), map_day("Thursday"), time(11, 15), time(1),
     "Lunch with John", "Cupertino"),

    ("Lunch with John in Cupertino on Thursday from 11a-1:30",
     map_day("Thursday"), map_day("Thursday"), time(11), time(13,30),
     "Lunch with John", "Cupertino"),

    ("Lunch with John in Cupertino on Thursday from 11a-1:30pm",
     map_day("Thursday"), map_day("Thursday"), time(11), time(13,30),
     "Lunch with John", "Cupertino"),
    
    ("Lunch with John in Cupertino on Thursday from 11a-1:00",
     map_day("Thursday"), map_day("Thursday"), time(11), time(13),
     "Lunch with John", "Cupertino"),
    
    ("Lunch with John in Cupertino on Thursday from 11a-1:00pm",
     map_day("Thursday"), map_day("Thursday"), time(11), time(13),
     "Lunch with John", "Cupertino"),
    
    ("Lunch with John in Cupertino on Thursday from 11pm-1",
     map_day("Thursday"), map_day("Thursday") + timedelta(days=1), time(23),
     time(1), "Lunch with John", "Cupertino"),
    
    ("Lunch with John in Cupertino on Thursday from 11p-1p",
     map_day("Thursday"), map_day("Thursday"), time(23), time(13),
     "Lunch with John", "Cupertino"),

    ("Lunch with John in Cupertino on Thursday from 11a-1pm",
     map_day("Thursday"), map_day("Thursday"), time(11), time(13),
     "Lunch with John", "Cupertino"),
    
    ("Lunch with John in Cupertino on Thursday from 11am-1A",
     map_day("Thursday"), map_day("Thursday") + timedelta(days=1), time(11),
     time(1), "Lunch with John", "Cupertino"),
    
    ("Lunch with John in Cupertino on Thursday From 11a-1am",
     map_day("Thursday"), map_day("Thursday") + timedelta(days=1), time(11),
     time(1), "Lunch with John", "Cupertino"),

    ("Lunch with John in Cupertino on Thursday from 11- 1:30pm",
     map_day("Thursday"), map_day("Thursday"), time(11), time(13,30),
     "Lunch with John", "Cupertino"),
    
    ("Lunch with John in Cupertino on Thursday from 11 -1",
     map_day("Thursday"), map_day("Thursday"), time(11), time(13),
     "Lunch with John", "Cupertino"),
    
    ("Lunch with John in Cupertino on Thursday from 11 - 1:30pm",
     map_day("Thursday"), map_day("Thursday"), time(11), time(13,30),
     "Lunch with John", "Cupertino"),

    ("Lunch with John in Cupertino on Thursday from 11pm",
     map_day("Thursday"), map_day("Thursday"), time(23), None,
     "Lunch with John", "Cupertino"),

    ("12p to 2p on May 5th, committee meeting", 
     next_day(5, 5), next_day(5, 5), time(12), time(14), "committee meeting",
     None),

    ("12p to 2p on 15th of may, committee meeting", 
     next_day(5, 15), next_day(5, 15), time(12), time(14), "committee meeting",
     None),

    ("12p to 2p on 15th of may, 2020 committee meeting", 
     date(2020, 5, 15), date(2020, 5, 15), time(12), time(14),
     "committee meeting", None),

    ("12p to 2p on May 5th, committee meeting at 559 Madison Ave.", 
     next_day(5, 5), next_day(5, 5), time(12), time(14), "committee meeting",
     "559 Madison Ave"),

    ("23rd of May at 2000 Elm St, Dinner with Andre", 
     next_day(5, 23), next_day(5, 23), time(20), None, "Dinner with Andre",
     "2000 Elm St"),

    ("November 23rd at 8:00p, Dinner with Andre at Toku", 
     next_day(11, 23), next_day(11, 23), time(20), None, "Dinner with Andre",
     "Toku"),

    ("January 24 at 3pm - 4:40pm Feb 3,  Retreat at Hilton Hotel", 
     next_day(1, 24), next_day(1, 24) + timedelta(days=10), time(15), 
     time(16, 40), "Retreat", "Hilton Hotel"),

    ("Christmas is on December 25th.", 
     next_day(12, 25), next_day(12, 25), None, None, "Christmas", None),

    ("Homework is due on the eleventh",
     next_monthday(11), next_monthday(11), None, None, "Homework due", None),

    ("Homework is due on the 11th",
     next_monthday(11), next_monthday(11), None, None, "Homework due", None),

    ("Homework is due on the 1st",
     next_monthday(1), next_monthday(1), None, None, "Homework due", None),

    ("Homework is due on June first",
     next_day(6, 1), next_day(6, 1), None, None, "Homework due", None),

    ("Homework is due on June 1st",
     next_day(6, 1), next_day(6, 1), None, None, "Homework due", None),
     
    ("Homework is due on June 1",
     next_day(6, 1), next_day(6, 1), None, None, "Homework due", None),

    ("Homework 5 due next monday at 3 o'clock at 4 Towne Hall", 
     map_day("Monday"), map_day("Monday"), time(15), None, "Homework 5 due",
     "4 Towne Hall"),

    ("Homework 5 due next sunday at 4 Towne Hall at 3pm", 
     map_day("Sunday"), map_day("Sunday"), time(15), None, "Homework 5 due",
     "4 Towne Hall"),

    ("Homework 5 due next monday at 4 Towne Hall at 3", 
     map_day("Monday"), map_day("Monday"), time(15), None, "Homework 5 due",
     "4 Towne Hall"),

    ("The retreat is from Jan 12 - 29, at The Beach House", 
     next_day(1, 12), next_day(1, 12) + timedelta(days=17), None, None, 
     "The retreat", "The Beach House"),

    ("Bake a cake tomorrow.", 
     tomorrow, tomorrow, None, None, "Bake a cake", None),

    ("Use Horizon today!", 
     today, today, None, None, "Use Horizon", None),

    ("At arena 2:00pm Football Game", 
     None, None, time(14), None, "Football Game", "arena"),

    ("Staff meeting on Monday at 9 am in the conference room", 
     map_day("Monday"), map_day("Monday"), time(9), None, "Staff meeting",
     "the conference room"),

    ("Project meeting with Jason 4 pm tomorrow at coffee shop", 
     tomorrow, tomorrow, time(16), None, "Project meeting with Jason",
     "coffee shop"),

    ("Let's have lunch at Joe's on the 3rd.", 
     next_monthday(3), next_monthday(3), None, None, "Let's have lunch",
     "Joe's"),

    ("Let's have lunch at Joe's on the 29th.", 
     next_monthday(29), next_monthday(29), None, None, "Let's have lunch",
     "Joe's"),

    ("Boys ski trip at Victor's from the 3rd to the 6th", 
     next_monthday(3), next_monthday(6), None, None, "Boys ski trip",
     "Victor's"),

    ("The exam is in a week", 
     today + timedelta(days=7), today + timedelta(days=7), None, None,
     "The exam", None),

    ("The exam is a week from Friday", 
     map_day("Friday") + timedelta(days=7),
     map_day("Friday") + timedelta(days=7), None, None, "The exam", None),

    ("The exam is in 2 weeks", 
     today + timedelta(days=14), today + timedelta(days=14), None, None,
     "The exam", None),

    ("The exam is in 3 weeks from tomorrow.", 
     today + timedelta(days=22), today + timedelta(days=22), None, None,
     "The exam", None),

    ("The exam is three weeks from tomorrow.", 
     today + timedelta(days=22), today + timedelta(days=22), None, None,
     "The exam", None),

    ("The exam is a week from yesterday", 
     today + timedelta(days=6), today + timedelta(days=6), None, None,
     "The exam", None),

    ("The exam is Wednesday @ 2pm and lasts for five hours", 
     map_day("Wednesday"), map_day("Wednesday"), time(14), time(19),
     "The exam", None),

    ("The operation is in a month", 
     in_x_months(1), in_x_months(1), None, None, "The operation", None),

    ("The operation is a month from Friday", 
     in_x_months(1, map_day("Friday")), in_x_months(1, map_day("Friday")),
     None, None, "The operation", None),

    ("The operation is in 2 months", 
     in_x_months(2), in_x_months(2), None, None, "The operation", None),

    ("The operation is 3 months from tomorrow.", 
     in_x_months(3, tomorrow), in_x_months(3, tomorrow), None, None,
     "The operation", None),

    ("The operation is in three months from tomorrow.", 
     in_x_months(3, tomorrow), in_x_months(3, tomorrow), None, None,
     "The operation", None),

    ("The operation is a month from yesterday", 
     in_x_months(1, yesterday), in_x_months(1, yesterday), None, None,
     "The operation", None),

    ("The koala will be set free on the fourth of july @noon", 
     next_day(7, 4), next_day(7, 4), time(12), None,
     "The koala will be set free", None),

    ("My mom's birthday is on the 27th", 
     next_monthday(27), next_monthday(27), None, None, "My mom's birthday",
     None),

    ("The biology exam is @ 8a and goes until 11", 
     None, None, time(8), time(11), "The biology exam", None),

    ("Meet Bill on the 5th at City Hall",
     next_monthday(5), next_monthday(5), None, None, "Meet Bill", "City Hall"),

    ("The conference is on Feb 12 at 3pm", 
     next_day(2, 12), next_day(2, 12), time(15), None, "The conference", None),

    ("Birthday party from midnight to noon on March fourth", 
     next_day(3, 4), next_day(3, 4), time(0), time(12), "Birthday party", None),

    ("Birthday party from midnight to noon on the fourth of March", 
     next_day(3, 4), next_day(3, 4), time(0), time(12), "Birthday party", None),

    ("High school admission results in 1 week", 
     today + timedelta(days=7), today + timedelta(days=7), None, None,
     "High school admission results", None),

    ("Lunch with John at 123 Main Street on Tuesday", 
     map_day("Tuesday"), map_day("Tuesday"), None, None, "Lunch with John",
     "123 Main Street"),

    ("Dinner at 6", 
     None, None, time(18), None, "Dinner", None),

    ("Dinner at 7", 
     None, None, time(19), None, "Dinner", None),

    ("Dinner at 8:15", 
     None, None, time(20,15), None, "Dinner", None),

    ("Breakfast at 6", 
     None, None, time(6), None, "Breakfast", None),

    ("Breakfast at 7", 
     None, None, time(7), None, "Breakfast", None),

    ("Breakfast at 8:15", 
     None, None, time(8,15), None, "Breakfast", None),

    ("Pick up Joe tomorrow at LAX at 8pm", 
     tomorrow, tomorrow, time(20), None, "Pick up Joe", "LAX"),

    ("Pick up Joe the day after tomorrow at LAX at 8pm", 
     tomorrow + timedelta(days=1), tomorrow + timedelta(days=1), time(20),
     None, "Pick up Joe", "LAX"),

    ("Go home the day after July 4", 
     next_day(7,5), next_day(7,5), None, None, "Go home", None),

    ("Cycling class @6 for 1.5h", 
     None, None, time(6), time(7, 30), "Cycling class", None),

    ("Cycling class @6 for 1.5 h", 
     None, None, time(6), time(7, 30), "Cycling class", None),

    ("Cycling class @6 for 1.5 hours", 
     None, None, time(6), time(7, 30), "Cycling class", None),

    ("Cycling class @6 for 2 hours", 
     None, None, time(6), time(8), "Cycling class", None),

    ("Next Tuesday Jogging in the Park @8a for 90 min", 
     map_day("Tuesday"), map_day("Tuesday"), time(8), time(9, 30), "Jogging",
     "the Park"),

    ("Trip to Turkey first of july through 5th of aug", 
     next_day(7, 1), next_day(7, 1) + timedelta(days=35), None, None,
     "Trip to Turkey", None),

    ("Trip to Turkey July 1 through 5th of aug", 
     next_day(7, 1), next_day(7, 1) + timedelta(days=35), None, None,
     "Trip to Turkey", None),

    ("Party Tuesday at Rob's House, 7-11p", 
     map_day("Tuesday"), map_day("Tuesday"), time(19), time(23), "Party",
     "Rob's House"),

    ("Party Tuesday at Rob's House, 7-11", 
     map_day("Tuesday"), map_day("Tuesday"), time(19), time(23), "Party",
     "Rob's House"),

    ("Lunch with Matthew at 600 Main St. at 1:30 Monday", 
     map_day("Monday"), map_day("Monday"), time(13, 30), None,
     "Lunch with Matthew", "600 Main St"),

    ("Final project due August 15", 
     next_day(8, 15), next_day(8, 15), None, None, "Final project due", None),

    ("Paper due next Wednesday", 
     map_day("Wednesday"), map_day("Wednesday"), None, None, "Paper due",
     None),

    ("Exam on February 27th at 5pm", 
     next_day(2, 27), next_day(2, 27), time(17), None, "Exam", None),

    ("Meeting at Noon next Thursday", 
     map_day("Thursday"), map_day("Thursday"), time(12), None, "Meeting",
     None),

    ("Buy milk tomorrow 5 to 6", 
     tomorrow, tomorrow, time(17), time(18), "Buy milk", None),

    ("Meet with Cody at Apple Store tomorrow from 5 to 6", 
     tomorrow, tomorrow, time(17), time(18), "Meet with Cody",
     "Apple Store"),

    ("Meet with Cody tomorrow at Apple Store from 5 to 6", 
     tomorrow, tomorrow, time(17), time(18), "Meet with Cody",
     "Apple Store"),

    ("Meet with Cody tomorrow 5 to 6 at Apple Store", 
     tomorrow, tomorrow, time(17), time(18), "Meet with Cody",
     "Apple Store"),

    ("Dinner with Rhiannon tomorrow 7pm at New Gen Sushi", 
     tomorrow, tomorrow, time(19), None, "Dinner with Rhiannon",
     "New Gen Sushi"),

    ("Brendan's 6th birthday party January 22 at 11:00 at our house.", 
     next_day(1, 22), next_day(1, 22), time(11), None,
     "Brendan's 6th birthday party", "our house"),

    ("Meeting from 5 - 6", 
     None, None, time(17), time(18), "Meeting", None),

    ("Meeting from 5 to 6", 
     None, None, time(17), time(18), "Meeting", None),

    ("Meeting from 5 until 6", 
     None, None, time(17), time(18), "Meeting", None),

    ("Meeting at 5 - 6 at Warren Weaver Hall, Rm 1306", 
     None, None, time(17), time(18), "Meeting",
     "Warren Weaver Hall, Rm 1306"),

    ("Meeting at 5 til 6 at Warren Weaver Hall", 
     None, None, time(17), time(18), "Meeting", "Warren Weaver Hall"),

    ("Meeting from 5 until 7 at Warren Weaver Hall", 
     None, None, time(17), time(19), "Meeting", "Warren Weaver Hall"),

    ("Meeting from 5 thru 7 at Warren Weaver Hall", 
     None, None, time(17), time(19), "Meeting", "Warren Weaver Hall"),

    ("Meeting from 5 through 7 at Warren Weaver Hall", 
     None, None, time(17), time(19), "Meeting", "Warren Weaver Hall"),

    ("Meeting from 5 to 7 at Warren Weaver Hall", 
     None, None, time(17), time(19), "Meeting", "Warren Weaver Hall"),

    ("Meeting from 5 till 7 at Warren Weaver Hall", 
     None, None, time(17), time(19), "Meeting", "Warren Weaver Hall"),

    ("Meeting at 5-630p", 
     None, None, time(17), time(18, 30), "Meeting", None), 

    ("Meeting at 5-630", 
     None, None, time(17), time(18, 30), "Meeting", None), 

    ("Meeting at 8-915p", 
     None, None, time(20), time(21, 15), "Meeting", None), 

    ("Meeting at 8 in the evening", 
     None, None, time(20), None, "Meeting", None), 

    ("Meeting at 8 in the morning", 
     None, None, time(8), None, "Meeting", None), 

    ("Swimming at 4 in the morning", 
     None, None, time(4), None, "Swimming", None), 

    ("Swimming at 4 in the afternoon", 
     None, None, time(16), None, "Swimming", None), 

    ("Swimming at 4:30 in the afternoon", 
     None, None, time(16,30), None, "Swimming", None), 

    ("Meeting at 9 at night", 
     None, None, time(21), None, "Meeting", None), 

    ("Meeting at 9 in the morning", 
     None, None, time(9), None, "Meeting", None), 

    ("Meeting at 9:00 in the morning", 
     None, None, time(9), None, "Meeting", None), 

    ("Training Friday 1100-1200 in the big tent",
     map_day("Friday"), map_day("Friday"), time(11), time(12), "Training",
     "the big tent"),

    ("Training Friday 1500-1730 in the big tent",
     map_day("Friday"), map_day("Friday"), time(15), time(17, 30), "Training",
     "the big tent"),

    ("Training Friday 1100-130p in the big tent",
     map_day("Friday"), map_day("Friday"), time(11), time(13, 30), "Training",
     "the big tent"),

    ("Fondue at Fondue Palace tomorrow at seven thirty pm", 
     tomorrow, tomorrow, time(19, 30), None, "Fondue", "Fondue Palace"),

    ("Fondue at seven o'clock at Fondue Palace", 
     None, None, time(19), None, "Fondue", "Fondue Palace"),

    ("Fondue at Fondue Palace at seven thirty", 
     None, None, time(19, 30), None, "Fondue", "Fondue Palace"),

    ("Fondue at seven at Fondue Palace", 
     None, None, time(19), None, "Fondue", "Fondue Palace"),

    ("Fondue at 7 at Fondue Palace", 
     None, None, time(19), None, "Fondue", "Fondue Palace"),

    ("Dinner with Rocko at Main Street from 6 to 7", 
     None, None, time(18), time(19), "Dinner with Rocko", "Main Street"),

    ("Dinner at 45 Hilldale Lane, Port Washington, NY from 6 to 8", 
     None, None, time(18), time(20), "Dinner",
     "45 Hilldale Lane, Port Washington, NY"),
     
    ("Lunch with Preshit tomorrow at 8 PM until 11:20", 
     tomorrow, tomorrow, time(20), time(23, 20), "Lunch with Preshit",
     None),

    ("Lunch with Preshit tomorrow at 8 until 11:20", 
     tomorrow, tomorrow, time(8), time(11, 20), "Lunch with Preshit",
     None),

    ("Lunch with Preshit tomorrow at 11 till 12:20", 
     tomorrow, tomorrow, time(11), time(12, 20), "Lunch with Preshit",
     None),

    ("Ski Corbet's Couloir tomorrow morning at 8", 
     tomorrow, tomorrow, time(8), None, "Ski Corbet's Couloir", None),

    ("Graduate Computer Graphics at NYU, West 4th St., New York, from 5 - 7", 
     None, None, time(17), time(19), "Graduate Computer Graphics",
     "NYU, West 4th St., New York"),

    ("Graduate Computer Graphics at NYU, 16 East 4th Street, New York, from 5 - 7", 
     None, None, time(17), time(19), "Graduate Computer Graphics",
     "NYU, 16 East 4th Street, New York"),

    ("At Laguna Beach, CA, United States, surfing lessons tue at 0800AM", 
     map_day("Tuesday"), map_day("Tuesday"), time(8), None, "surfing lessons",
     "Laguna Beach, CA, United States"),

    ("Star gazing with Jen at the Custer Observatory, Southold, NY on Saturday from 10-11pm", 
     map_day("Saturday"), map_day("Saturday"), time(22), time(23),
     "Star gazing with Jen", "the Custer Observatory, Southold, NY"),

    ("WWDC at Moscone West, San Francisco, CA June 11th to 15th", 
     next_day(6, 11), next_day(6, 11) + timedelta(days=4), None, None,
     "WWDC", "Moscone West, San Francisco, CA"),

    ("dec 1 at 3pm - 11", 
     next_day(12, 1), next_day(12, 1), time(15), time(23), None, None),

    ("dec 1 from 3pm - 11", 
     next_day(12, 1), next_day(12, 1), time(15), time(23), None, None),

    ("dec 1 from 3pm to 11", 
     next_day(12, 1), next_day(12, 1), time(15), time(23), None, None),

    ("dec 1 from 3 to 11p", 
     next_day(12, 1), next_day(12, 1), time(15), time(23), None, None),

    ("jan 1st at 9am through january fifth 8pm", 
     next_day(1, 1), next_day(1,1) + timedelta(days=4), time(9), time(20),
     None, None),

    ("Lunch with becca at cafe thu 1-2", 
     map_day("Thursday"), map_day("Thursday"), time(13), time(14),
     "Lunch with becca", "cafe"),

    ("lunch with John at \"Taco Tuesdays\" Friday 12 pm", 
     map_day("Friday"), map_day("Friday"), time(12), None, "lunch with John",
     "\"Taco Tuesdays\""),

    ("Volleyball at 5pm", 
     None, None, time(17), None, "Volleyball", None), 

    ("Bank holiday 8/14/2019 no school", 
     date(2019, 8, 14), date(2019, 8, 14), None, None,
     "Bank holiday no school", None),

    ("Staff meeting next Monday at 13:00", 
     map_day("Monday"), map_day("Monday"), time(13), None, "Staff meeting",
     None), 

    ("Running w/ Pat 2:15 tomorrow for 45 minutes", 
     tomorrow, tomorrow, time(14, 15), time(15), "Running w/ Pat",
     None),

    ("Running w/ Pat in 2 hours", 
     today, today, in_x_min(120), None, "Running w/ Pat", None),

    ("Running w/ Pat in 20 MIN", 
     today, today, in_x_min(20), None, "Running w/ Pat", None),

    ("Running w/ Pat in 2.5 hours", 
     today, today, in_x_min(150), None, "Running w/ Pat", None),

    ("Running with Pat 2:15 - 3 pm tomorrow", 
     tomorrow, tomorrow, time(14, 15), time(15), "Running with Pat", None),

    ("National Conference 9/23 - 9/26 in Atlanta", 
     next_day(9, 23), next_day(9, 23) + timedelta(days=3), None, None,
     "National Conference", "Atlanta"),

    ("Tennis practice Tuesday 7pm to 9pm", 
     map_day("Tuesday"), map_day("Tuesday"), time(19), time(21),
     "Tennis practice", None),

    ("Language Class Wednesday 7-8pm", 
     map_day("Wednesday"), map_day("Wednesday"), time(19), time(20),
     "Language Class", None), 

    ("Appointment at Somewhere on June 3rd 10am-10:25am", 
     next_day(6, 3), next_day(6, 3), time(10), time(10,25), "Appointment",
     "Somewhere"),

    ("Lunch tomorrow 15:00 in room 2", 
     tomorrow, tomorrow, time(15), None, "Lunch", "room 2"),

    ("Lunch with English Project Team at Fountain Dining Hall 12:15pm Thursday", 
     map_day("Thursday"), map_day("Thursday"), time(12, 15), None,
     "Lunch with English Project Team", "Fountain Dining Hall"),

    ("Test event on 3/13 at 245 until 4 at 666 Main Street", 
     next_day(3, 13), next_day(3, 13), time(14, 45), time(16), "Test event",
     "666 Main Street"),

    ("Conference call Monday 9am", 
     map_day("Monday"), map_day("Monday"), time(9), None, "Conference call",
     None),

    ("Workout at Power 10 Thursday at 11:30", 
     map_day("Thursday"), map_day("Thursday"), time(11, 30), None, "Workout",
     "Power 10"),

    ("Call John Bates to apologize tomorrow at 9", 
     tomorrow, tomorrow, time(9), None, "Call John Bates to apologize", None),

    ("Call John Bates with apology tomorrow at 9", 
     tomorrow, tomorrow, time(9), None, "Call John Bates with apology", None),

    ("breakfast with Kohli tomorrow at 4 to 8 am", 
     tomorrow, tomorrow, time(4), time(8), "breakfast with Kohli", None),

    ("Tennis with David and Shaun saturday at 10:30", 
     map_day("Saturday"), map_day("Saturday"), time(10, 30), None,
     "Tennis with David and Shaun", None),

    ("Meeting with Johnny, Marco, and Alexandri to talk about the research 5pm tomorrow", 
     tomorrow, tomorrow, time(17), None,
     "Meeting with Johnny, Marco, and Alexandri to talk about the research",
     None),

    ("At the plaza Monday, talk to Joe about money laundering from 6:30Pm to 8", 
     map_day("Monday"), map_day("Monday"), time(18, 30), time(20),
     "talk to Joe about money laundering", "the plaza"),

    ("Dinner with Ben Kerwing 2 weeks from wednesday at Lupa from 7 to 9", 
     map_day("Wednesday") + timedelta(days=14),
     map_day("Wednesday") + timedelta(days=14), time(19), time(21),
     "Dinner with Ben Kerwing", "Lupa"),

    ("Dinner with Ben Kerwing two weeks from wednesday at Lupa from 7 to 9", 
     map_day("Wednesday") + timedelta(days=14),
     map_day("Wednesday") + timedelta(days=14), time(19), time(21),
     "Dinner with Ben Kerwing", "Lupa"),

    ("dinner with Erin tomorrow evening", 
     tomorrow, tomorrow, None, None, "dinner with Erin", None),

    ("at Los Angeles from 5-6 test with paul", 
     None, None, time(17), time(18), "test with paul", "Los Angeles"),

    ("in Los Angeles, from 5 to 6 test with paul", 
     None, None, time(17), time(18), "test with paul", "Los Angeles"),

    ("Brunch for Amanda's birthday in Williamsburg April 28th at 12:00p", 
     next_day(4, 28), next_day(4, 28), time(12), None,
     "Brunch for Amanda's birthday", "Williamsburg"),

    ("Bob's 25th anniversary on May, 14th 2020", 
     date(2020, 5, 14), date(2020, 5, 14), None, None,
     "Bob's 25th anniversary", None),

    ("Meeting is Tuesday 8:00-10:00",
     map_day("Tuesday"), map_day("Tuesday"), time(8), time(10), "Meeting",
     None),
     
    ("Discuss project plan Wednesday 8:00am-10:00am",
     map_day("Wednesday"), map_day("Wednesday"), time(8), time(10),
     "Discuss project plan", None),

    ("Discuss project plan Wednesday 8:00-10:00am",
     map_day("Wednesday"), map_day("Wednesday"), time(8), time(10),
     "Discuss project plan", None),

    ("Discuss project plan Wednesday 8:00am-10:00",
     map_day("Wednesday"), map_day("Wednesday"), time(8), time(10),
     "Discuss project plan", None),
     
    ("Discuss project plan Wednesday 8:00-10:00a.m.",
     map_day("Wednesday"), map_day("Wednesday"), time(8), time(10),
     "Discuss project plan", None),

    ("Discuss project plan Wednesday 8:00-10:00 a.m.",
     map_day("Wednesday"), map_day("Wednesday"), time(8), time(10),
     "Discuss project plan", None),
     
    ("Discuss project plan Wednesday 8:00-10:00 p.m.",
     map_day("Wednesday"), map_day("Wednesday"), time(20), time(22),
     "Discuss project plan", None),
     
    ("Discuss project plan Wednesday 8:00:00-10:00:00",
     map_day("Wednesday"), map_day("Wednesday"), time(8), time(10),
     "Discuss project plan", None),

    ("Discuss project plan Wed 8:00:00p-10:00:00p",
     map_day("Wednesday"), map_day("Wednesday"), time(20), time(22),
     "Discuss project plan", None),     

    ("Discuss project plan Weds 8-10:00:00p",
     map_day("Wednesday"), map_day("Wednesday"), time(20), time(22),
     "Discuss project plan", None),     
     
#    ("Discuss project plan Weds 13p  #error",   TODO
     
    ("Discuss project plan Weds 130p",
     map_day("Wednesday"), map_day("Wednesday"), time(13,30), None,
     "Discuss project plan", None),
     
    ("Discuss project plan Weds 1230p",
     map_day("Wednesday"), map_day("Wednesday"), time(12,30), None,
     "Discuss project plan", None),

    ("Meet Thursday 8:30-10",
     map_day("Thursday"), map_day("Thursday"), time(8,30), time(10), "Meet",
     None),

    ("Meet Thursday 8:30AM-10",
     map_day("Thursday"), map_day("Thursday"), time(8,30), time(10), "Meet",
     None),
     
    ("Meet Thursday 8:30p-10",
     map_day("Thursday"), map_day("Thursday"), time(20,30), time(22), "Meet",
     None),
     
    ("Meet Thursday 8p-10",
     map_day("Thursday"), map_day("Thursday"), time(20), time(22), "Meet",
     None),
     
    ("Meet Th 8p-10",
     map_day("Thursday"), map_day("Thursday"), time(20), time(22), "Meet",
     None),
     
    ("Run Friday 8-10 a.m.",
     map_day("Friday"), map_day("Friday"), time(8), time(10), "Run", None),
     
    ("Run Friday 8-10 AM",
     map_day("Friday"), map_day("Friday"), time(8), time(10), "Run", None),

    ("Run Friday 8-10 a",
     map_day("Friday"), map_day("Friday"), time(8), time(10), "Run", None),
     
    ("Run Friday 8:00",
     map_day("Friday"), map_day("Friday"), time(8), None, "Run", None),
     
    ("Run Friday 8:00AM",
     map_day("Friday"), map_day("Friday"), time(8), None, "Run", None),
     
    ("Run Friday 8:00A.M.",
     map_day("Friday"), map_day("Friday"), time(8), None, "Run", None),
     
    ("Dance Sat 3p",
     map_day("Saturday"), map_day("Saturday"), time(15), None, "Dance", None),
     
    ("Dance Saturday 3P",
     map_day("Saturday"), map_day("Saturday"), time(15), None, "Dance", None),
     
    ("Dance sat 11p",
     map_day("Saturday"), map_day("Saturday"), time(23), None, "Dance", None),
     
    ("Cooking class Sunday 3o'clock",
     map_day("Sunday"), map_day("Sunday"), time(15), None, "Cooking class",
     None),
     
    ("Cooking class Sunday 3oclock",
     map_day("Sunday"), map_day("Sunday"), time(15), None, "Cooking class",
     None),
     
    ("Cooking class Sun 3 O'Clock",
     map_day("Sunday"), map_day("Sunday"), time(15), None, "Cooking class",
     None),
     
    ("Cooking class Sun 3 Oclock",
     map_day("Sunday"), map_day("Sunday"), time(15), None, "Cooking class",
     None),
     
    ("Labor day 9/3/18",
     date(2018, 9, 3), date(2018, 9, 3), None, None, "Labor day", None),
     
    ("Labor day 09/03/18",
     date(2018, 9, 3), date(2018, 9, 3), None, None, "Labor day", None),
     
    ("Labor day 09/03/2018",
     date(2018, 9, 3), date(2018, 9, 3), None, None, "Labor day", None),
     
    ("Labor day is 2018/9/3",
     date(2018, 9, 3), date(2018, 9, 3), None, None, "Labor day", None),
     
    ("Labor day is 2018/09/03",
     date(2018, 9, 3), date(2018, 9, 3), None, None, "Labor day", None),
     
    ("Vacation 7/2-7/13",
     next_day(7,2), next_day(7,2) + timedelta(days=11), None, None, "Vacation",
     None),
     
    ("Vacation 7/2/2019-7/13",
     date(2019,7,2), date(2019,7,13), None, None, "Vacation", None),
     
    ("Vacation 10/2-10/9/19",
     date(2019,10,2), date(2019,10,9), None, None, "Vacation", None),
     
    ("Vacation October 2 thru October 9",
     next_day(10,2), next_day(10,2)+timedelta(days=7), None, None, "Vacation",
     None),
     
#    ("Vacation 13/24   # error",  TODO
     
    ("Labor day 9-3-18",
     date(2018, 9, 3), date(2018, 9, 3), None, None, "Labor day", None),
     
    ("Labor day 09-03-18",
     date(2018, 9, 3), date(2018, 9, 3), None, None, "Labor day", None),
     
    ("Labor day 09-03-2018",
     date(2018, 9, 3), date(2018, 9, 3), None, None, "Labor day", None),
     
    ("Labor day is 2018-09-03",
     date(2018, 9, 3), date(2018, 9, 3), None, None, "Labor day", None),
     
#    ("Vacation 13-24   # error",  TODO
     
    ("Labor day is 3 September 2018",
     date(2018, 9, 3), date(2018, 9, 3), None, None, "Labor day", None),
     
    ("Labor day is 3 September 18",
     date(2018, 9, 3), date(2018, 9, 3), None, None, "Labor day", None),
     
    ("Labor day is September 3, 18",
     date(2018, 9, 3), date(2018, 9, 3), None, None, "Labor day", None),
     
    ("Labor day is Sept 3, 2018",
     date(2018, 9, 3), date(2018, 9, 3), None, None, "Labor day", None),
     
    ("Labor day is Sep 3 2018",
     date(2018, 9, 3), date(2018, 9, 3), None, None, "Labor day", None),
     
    ("Liz's birthday is Jan twenty-seven",
     next_day(1, 27), next_day(1, 27), None, None, "Liz's birthday", None),
     
    ("Liz's birthday is January 27",
     next_day(1, 27), next_day(1, 27), None, None, "Liz's birthday", None),
     
    ("Liz's birthday is Feb 27",
     next_day(2, 27), next_day(2, 27), None, None, "Liz's birthday", None),
     
    ("Liz's birthday is February 27",
     next_day(2, 27), next_day(2, 27), None, None, "Liz's birthday", None),
     
    ("Liz's birthday is March 10",
     next_day(3, 10), next_day(3, 10), None, None, "Liz's birthday", None),
     
    ("Liz's birthday is Mar 10",
     next_day(3, 10), next_day(3, 10), None, None, "Liz's birthday", None),
     
    ("Doug's birthday is April 20",
     next_day(4, 20), next_day(4, 20), None, None, "Doug's birthday", None),
     
    ("Doug's birthday is on 20 Apr",
     next_day(4, 20), next_day(4, 20), None, None, "Doug's birthday", None),
     
    ("Doug's birthday is May ten",
     next_day(5, 10), next_day(5, 10), None, None, "Doug's birthday", None),
     
    ("Doug's birthday is the tenth of May",
     next_day(5, 10), next_day(5, 10), None, None, "Doug's birthday", None),
     
    ("Doug's birthday is on the tenth of May",
     next_day(5, 10), next_day(5, 10), None, None, "Doug's birthday", None),
     
    ("Mom's birthday is June 22",
     next_day(6,22), next_day(6,22), None, None, "Mom's birthday", None),
     
    ("Mom's birthday is 22 Jun",
     next_day(6,22), next_day(6,22), None, None, "Mom's birthday", None),
     
    ("Mom's birthday is July 22",
     next_day(7,22), next_day(7,22), None, None, "Mom's birthday", None),
     
    ("Mom's birthday is 22 Jul",
     next_day(7,22), next_day(7,22), None, None, "Mom's birthday", None),
     
    ("April's birthday is August seven",
     next_day(8,7), next_day(8,7), None, None, "April's birthday", None),
     
    ("April's birthday is 7 aug",
     next_day(8,7), next_day(8,7), None, None, "April's birthday", None),
     
    ("April wedding shower on Sep 3",
     next_day(9,3), next_day(9,3), None, None, "April wedding shower", None),

    ("Dad's birthday is oct 24, 1937",
     date(1937, 10, 24), date(1937, 10, 24), None, None, "Dad's birthday",
     None),
     
    ("Dad's birthday is 24 October 1937",
     date(1937, 10, 24), date(1937, 10, 24), None, None, "Dad's birthday",
     None),
     
    ("Thanksgiving is November 23 2017",
     date(2017, 11, 23), date(2017, 11, 23), None, None, "Thanksgiving", None),
     
    ("Thanksgiving is 23 November, 2017",
     date(2017, 11, 23), date(2017, 11, 23), None, None, "Thanksgiving", None),
     
    ("Thanksgiving is 23 Nov",
     next_day(11, 23), next_day(11, 23), None, None, "Thanksgiving", None),
     
    ("Thanksgiving is Nov 23",
     next_day(11, 23), next_day(11, 23), None, None, "Thanksgiving", None),
     
    ("The choir concert is on Dec 10",
     next_day(12, 10), next_day(12, 10), None, None, "The choir concert",
     None),
     
    ("The choir concert is on 10 December",
     next_day(12, 10), next_day(12, 10), None, None, "The choir concert",
     None),
     
    ("Winter break is Dec 20 til Jan 3",
     next_day(12,20), next_day(12,20) + timedelta(days=14), None, None,
     "Winter break", None),
     
    ("Winter break is 12/20 until 1/3",
     next_day(12,20), next_day(12,20) + timedelta(days=14), None, None,
     "Winter break", None),
     
    ("My vacation is in two weeks",
     today+timedelta(days=14), today+timedelta(days=14), None, None,
     "My vacation", None),
     
    ("My vacation starts in a month",
     in_x_months(1), in_x_months(1), None, None, "My vacation starts", None),

    ("Dinner at TGI Friday on tue at 7 to 8:30",
     map_day("Tuesday"), map_day("Tuesday"), time(19), time(20,30), "Dinner",
     "TGI Friday"),

    ("Meet at Ruby Tuesday on Weds at noon",
     map_day("Wednesday"), map_day("Wednesday"), time(12), None, "Meet",
     "Ruby Tuesday"),

    ("mimosas at Vasu's in two days at 6p",
     today + timedelta(days=2), today + timedelta(days=2), time(18), None,
     "mimosas", "Vasu's"),

    ("mimosas at Vasu's in 3 d at 6p",
     today + timedelta(days=3), today + timedelta(days=3), time(18), None,
     "mimosas", "Vasu's"),

    ("mimosas at Vasu's in a day at 6p",
     tomorrow, tomorrow, time(18), None, "mimosas", "Vasu's")
]
     
for t in testdata:
    assert len(t) == 7, t
