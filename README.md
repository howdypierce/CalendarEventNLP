# Natural Language Processing for Calendar Events

Python code that parses human-language phrases to extract calendar
events. Two parsing functions are provided:

* `parse_event()` parses a string to a tuple containing the event info.
	See documentation in the file event_parser.py.

* `parse_to_google_calendar()` is a wrapper around `event_parse()`,
  which returns a URL representing a Google calendar event. Opening
  this URL will bring up Google's new event details page for the
  parsed string. See documentation in the file google_calendar.py.

## Limitations

Currently, the code here parses English-language natural phrases, and
moreover it assumes US-style dates and times (so, for instance "3/4"
will be parsed as March 4 and not April 3).

It does not yet handle time zones in the input phrase, nor does it
handle recurring events.

It does not yet attempt to parse other meeting participants out of the
phrase and add them to the invite list. Doing so will probably require
access to the user's contacts database.

## Files

Since this is a quick-and-dirty research project, I haven't taken the
time to structure the code as a clean pip-installable module. Here's a
description of the various files to get you started:

* `event_parser.py`: The main parsing code

* `google_calendar.py`: Wrapper code for parsing phrases to Google Calendar events

* `spelled_numbers.py`: Translates spelled-out numbers to digits

* `etoken.py`: Underlying data structure for "event tokens" (basically words)

* `event_parser_test.py`: An executable that runs tests against event_parser.py

* `testdata.py`: Test cases, used by event_parser_test.py

## Dependencies

This code relies on [NLTK](https://www.nltk.org/) for initial sentence parsing and
part-of-speech identification.

## License and Contributions

This project is freely licensed under the GPLv3. See the file LICENSE
for details. Bug reports and contributions are welcome.
