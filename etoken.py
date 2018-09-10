# etoken.py: Word token class abstraction 
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


class EToken():
    """One token in the string being parsed. 

    A token has the following attributes (all of type string unless noted):

    .orig
        The original form, exactly as input by the user
    .val
        The processed form of the token. In lower case, and possibly
        with other transformations done to make it more parsable.
    .pos
        The parsed Part of Speech; see below for possible values
    .sem
        The semantic role of this token, from this set of values
           DATE, ST_DATE, END_DATE 
           TIME, ST_TIME, END_TIME
           TITLE
           LOCATION
           DURATION
           IGN  (means "should be ignored")
           - (means "unknown")

    Here is the current table of .pos (part-of-speech) values:

        CC	coordinating conjunction
        CD	cardinal digit
        DT	determiner
        EX	existential there (like: "there is" ... like "there exists")
        FW	foreign word
        IN	preposition/subordinating conjunction
        JJ	adjective	'big'
        JJR	adjective, comparative	'bigger'
        JJS	adjective, superlative	'biggest'
        LS	list marker	1)
        MD	modal	could, will
        NN	noun, singular 'desk'
        NNS	noun plural	'desks'
        NNP	proper noun, singular	'Harrison'
        NNPS	proper noun, plural	'Americans'
        OD      ordinal digit
        PDT	predeterminer	'all the kids'
        POS	possessive ending	parent's
        PRP	personal pronoun	I, he, she
        PRP$	possessive pronoun	my, his, hers
        RB	adverb	very, silently,
        RBR	adverb, comparative	better
        RBS	adverb, superlative	best
        RP	particle	give up
        TO	to	go 'to' the store.
        UH	interjection	errrrrrrrm
        VB	verb, base form	take
        VBD	verb, past tense	took
        VBG	verb, gerund/present participle	taking
        VBN	verb, past participle	taken
        VBP	verb, sing. present, non-3d	take
        VBZ	verb, 3rd person sing. present	takes
        WDT	wh-determiner	which
        WP	wh-pronoun	who, what
        WP$	possessive wh-pronoun	whose
        WRB	wh-abverb	where, when
    """

    def __init__(self, orig_str: str, pos: str, sem: str = "-"):
        self.orig = orig_str
        self.val = orig_str.lower()
        self.pos = pos
        self.sem = sem
        self._time = None  # filled in for date tokens
        self._date = None  # filled in for time tokens

    def __repr__(self):
        if self._time:
            return(f"{self._time}({self.sem})")
        if self._date:
            return(f"{self._date}({self.sem})")
        return (f"{self.val}({self.sem},{self.pos})")

    time_sems = ["TIME", "ST_TIME", "END_TIME"]
    date_sems = ["DATE", "ST_DATE", "END_DATE"]

    @property
    def time(self):
        return self._time
    
    @time.setter
    def time(self, x):
        self._time = x
        if self.sem not in __class__.time_sems:
            self.sem = "TIME"
    
    @property
    def date(self):
        return self._date
    
    @date.setter
    def date(self, x):
        self._date = x
        if self.sem not in __class__.date_sems:
            self.sem = "DATE"

    def match(self, val = None, pos = None, sem = None) -> bool:
        """If this token matches all the supplied values, return True.

        val, pos, and sem can all be either None (matches everything),
        a single string (must match), a list of strings (must match
        one element on the list), or a dict (must be one of the keys
        in the dict).
        """
        if type(val) is str and self.val != val:
            return False
        if type(val) is list and self.val not in val:
            return False
        if type(val) is dict and self.val not in val:
            return False

        if type(pos) is str and self.pos != pos:
            return False
        if type(pos) is list and self.pos not in pos:
            return False
        if type(pos) is dict and self.pos not in pos:
            return False

        if type(sem) is str and self.sem != sem:
            return False
        if type(sem) is list and self.sem not in sem:
            return False
        if type(sem) is dict and self.sem not in sem:
            return False

        return True


class ETokenNull():
    """EToken lookalike that it has no contents and its match function
    always returns False. Convenient for parsing.
    """
    def __init__(self):
        self.orig = "NULL"
        self.val = "NULL"
        self.pos = "NULL"
        self.sem = "NULL"
        self.time = None
        self.date = None

    def __repr__(self):
        return (f"NULL")

    def match(self, val = None, pos = None, sem = None) -> bool:
        """Always returns False"""
        return False


def padded(seq, target_length, padding=ETokenNull()):
    """Return a copy of the sequence seq, extended padding (default:
    ETokenNull) so as to make its length up to target_length. If seq
    is already longer than target_length, just return a copy of it.
    """
    length = len(seq)
    ret = seq[:]
    if length < target_length:
        ret.extend([padding] * (target_length - length))
    return ret


