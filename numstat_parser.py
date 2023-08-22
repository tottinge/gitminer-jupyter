import re
from datetime import datetime
from typing import Optional

from gitminer import CommitNode


def read_all_commits(source):
    parser = NumstatParser()
    for line in source:
        parser.feed(line.rstrip())
        if parser.can_emit:
            yield parser.emit()
    if parser.can_emit:
        yield parser.emit()


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
        self.commit = CommitNode('', '', datetime.min)
        self.filestats = []
        self.can_emit = 0

    @property
    def hash(self):
        return self.commit.hash

    @hash.setter
    def hash(self, var):
        self.commit.hash = var

    @property
    def author(self):
        return self.commit.author

    @author.setter
    def author(self, var):
        self.commit.author = var

    @property
    def date(self):
        return self.commit.date

    @date.setter
    def date(self, val):
        self.commit.date = val

    def has_record(self):
        return all([
            self.commit.hash,
            self.commit.author,
            self.commit.message,
            self.can_emit
        ])

    def feed(self, line):
        self.state.feed(self, line)

    def emit(self):
        commit = CommitNode(self.hash, self.comment, self.date)
        files = self.filestats
        self.clear_fields()
        return commit, files

    def clear_fields(self):
        self.commit = CommitNode()
        self.can_emit = False
        self.filestats = []


class ParseError(Exception):
    ...
