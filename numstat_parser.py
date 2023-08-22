import re
from datetime import datetime
from typing import Optional


class ReadyState:
    def feed(self, sm, line):
        if not line.strip():
            return
        if line.startswith("commit"):
            sm.can_emit = False
            sm.hash = line.split()[-1]
            sm.state = ReadyForAuthor()
        else:
            raise ParseError()


class ReadyForAuthor:
    expected = re.compile(r"[Aa]uthor: .* <(.*)>")

    def feed(self, sm, line):
        line = line.strip()
        if not (m := self.expected.match(line)):
            raise ParseError()
        sm.author = m[1]
        sm.state = ReadyForDateState()


class ReadyForDateState:
    git_format = "%a %b %d %H:%M:%S %Y %z"

    def feed(self, sm, line: str):
        if not line.startswith('Date:'):
            raise ParseError()
        _, date_part = line.split(':', 1)
        sm.date = datetime.strptime(date_part.strip(), self.git_format)
        sm.state = CollectingCommentState()


class CollectingCommentState:
    def __init__(self):
        self.collecting: Optional[str] = None

    def feed(self, sm, line: str):
        if line.strip() == '':
            if self.collecting is None:
                return
            sm.comment = self.collecting
            sm.state = CollectingFileStatsState()
        if line.startswith('  '):
            usable = line.strip()
            self.collecting = (usable
                               if self.collecting is None
                               else "\n".join([self.collecting, usable])
                               )


class CollectingFileStatsState:
    def __init__(self):
        self.collected = []

    def feed(self, sm, line: str):
        if line.strip() == "":
            sm.filestats = self.collected
            sm.state = ReadyState()
            sm.can_emit = True;
            return
        try:
            _, _, filename = line.split()
            self.collected.append(filename)
        except ValueError as err:
            raise ParseError(err)


class NumstatParser:
    def __init__(self):
        self.state = ReadyState()
        self.hash: Optional[str] = None
        self.author: Optional[str] = None
        self.date: Optional[datetime] = None
        self.comment: Optional[str] = None
        self.filestats = []
        self.can_emit = 0

    def has_record(self):
        return all([
            self.hash,
            self.author,
            self.date,
            self.comment
        ])

    def feed(self, line):
        self.state.feed(self, line)

    def emit(self):
        # To implement next
        pass


class ParseError(Exception):
    ...
