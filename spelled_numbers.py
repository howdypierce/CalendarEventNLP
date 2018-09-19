# spelled_numbers.py: parse spelled numbers
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


from etoken import EToken

cardinals_to_num = {"one": "1",
                    "two": "2",
                    "three": "3",
                    "four": "4",
                    "five": "5",
                    "six": "6",
                    "seven": "7",
                    "eight": "8",
                    "nine": "9",
                    "ten": "10",
                    "eleven": "11",
                    "twelve": "12",
                    "thirteen": "13",
                    "fourteen": "14",
                    "fifteen": "15",
                    "sixteen": "16",
                    "seventeen": "17",
                    "eighteen": "18",
                    "nineteen": "19",
                    "twenty": "20",
                    "twentyone": "21",
                    "twenty-one": "21",
                    "twentytwo": "22",
                    "twenty-two": "22",
                    "twentythree": "23",
                    "twenty-three": "23",
                    "twentyfour": "24",
                    "twenty-four": "24",
                    "twentyfive": "25",
                    "twenty-five": "25",
                    "twentysix": "26",
                    "twenty-six": "26",
                    "twentyseven": "27",
                    "twenty-seven": "27",
                    "twentyeight": "28",
                    "twenty-eight": "28",
                    "twentynine": "29",
                    "twenty-nine": "29",
                    "thirty": "30",
                    "thirtyone": "31",
                    "thirty-one": "31"}

ordinals_to_num = {"first": "1",
                   "1st": "1",
                   "second": "2",
                   "2nd": "2",
                   "third": "3",
                   "3rd": "3",
                   "fourth": "4",
                   "4th": "4",
                   "fifth": "5",
                   "5th": "5",
                   "sixth": "6",
                   "6th": "6",
                   "seventh": "7",
                   "7th": "7",
                   "eighth": "8",
                   "8th": "8",
                   "ninth": "9",
                   "9th": "9",
                   "tenth": "10",
                   "10th": "10",
                   "eleventh": "11",
                   "11th": "11",
                   "twelfth": "12",
                   "12th": "12",
                   "thirteenth": "13",
                   "13th": "13",
                   "fourteenth": "14",
                   "14th": "14",
                   "fifteenth": "15",
                   "15th": "15",
                   "sixteenth": "16",
                   "16th": "16",
                   "seventeenth": "17",
                   "17th": "17",
                   "eighteenth": "18",
                   "18th": "18",
                   "nineteenth": "19",
                   "19th": "19",
                   "twentieth": "20",
                   "20th": "20",
                   "twentyfirst": "21",
                   "twenty-first": "21",
                   "21st": "21",
                   "twentysecond": "22",
                   "twenty-second": "22",
                   "22nd": "22",
                   "twentythird": "23",
                   "twenty-third": "23",
                   "23rd": "23",
                   "twentyfourth": "24",
                   "twenty-fourth": "24",
                   "24th": "24",
                   "twentyfifth": "25",
                   "twenty-fifth": "25",
                   "25th": "25",
                   "twentysixth": "26",
                   "twenty-sixth": "26",
                   "26th": "26",
                   "twentyseventh": "27",
                   "twenty-seventh": "27",
                   "27th": "27",
                   "twentyeighth": "28",
                   "twenty-eighth": "28",
                   "28th": "28",
                   "twentyninth": "29",
                   "twenty-ninth": "29",
                   "29th": "29",
                   "thirtieth": "30",
                   "30th": "30",
                   "thirtyfirst": "31",
                   "thirty-first": "31",
                   "31st": "31"}


def handle_spelled_number(tok: EToken) -> None:
    """Try to parse the token as a (partially) spelled number.

    This function finds spelled-out tokens that represent numbers, or
    a mix of digits and letters.

    These example strings should all be handled here:
       one
       ten
        (and so on, up to 31)

       first
       1st
       twenty-second
       22nd
        (and so on, up to 31)

    If there's a match, the .val will be replaced by a digit
    representation of the value, and the .pos will be set to either CD
    or OD as appropriate.
    """

    if tok.val in cardinals_to_num:
        tok.pos = "CD"
        tok.val = cardinals_to_num[tok.val]

    elif tok.val in ordinals_to_num:
        tok.pos = "OD"
        tok.val = ordinals_to_num[tok.val]

    return
