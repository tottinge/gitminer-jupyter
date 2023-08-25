import re
from datetime import datetime
from typing import Optional, Protocol, Any, Tuple, List

from gitminer import CommitNode


class ParseError(Exception):
    ...


def read_whole_commit(source):
    """
    Gitlogs are weird. sometimes they forget to add
    newlines, sometimes they leave out sections, and
    sometimes they are just a little wrong one way or another
    So, we read commit-to-commit first.
    """
    holding = []
    for line in source:
        if line.startswith('commit'):
            if holding:
                yield holding
                holding = []
        holding.append(line)
    if holding:
        yield holding

class NumstatParserState(Protocol):
    def feed(self, sm: Any, line: str) -> None:
        ...


def read_all_commits(source):
    for block in read_whole_commit(source):
        parser = NumstatParser()
        for line in block:
            try:
                parser.feed(line.rstrip('\r\n'))
            except Exception as err:
                print(err)
        if parser.can_emit:
            yield parser.emit()


class NumstatParser:
    def __init__(self):
        self.state: NumstatParserState = ReadyState()
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
        return self.commit.timestamp

    @date.setter
    def date(self, val):
        self.commit.timestamp = val

    @property
    def comment(self):
        return self.commit.message

    @comment.setter
    def comment(self, var):
        self.commit.message = var

    def has_record(self):
        return all([
            self.commit.hash,
            self.commit.author,
            self.commit.message,
            self.can_emit
        ])

    def feed(self, line):
        self.state.feed(self, line)

    def emit(self) -> Tuple[CommitNode, List[str]]:
        commit = CommitNode(self.hash, self.comment, self.date)
        files = self.filestats
        self.clear_fields()
        return commit, files

    def clear_fields(self):
        self.commit = CommitNode()
        self.can_emit = False
        self.filestats = []


class ReadyState:
    def feed(self, sm: NumstatParser, line: str) -> None:
        if not line.strip():
            return
        if line.startswith("commit"):
            sm.can_emit = False
            sm.hash = line.split()[-1]
            sm.state = ReadyForAuthor()
        elif line.strip().startswith("#"):
            return
        else:
            raise ParseError(f"Expecting commit, surprised by [{line}]")


class ReadyForAuthor:
    expected = re.compile(r"[Aa]uthor: .* <(.*)>")

    def feed(self, sm: NumstatParser, line: str):
        line = line.strip()
        if line.startswith("Merge:"):
            sm.state = IgnoringRecord()
            return
        if not (m := self.expected.match(line)):
            raise ParseError(f"looking for author in [{line}], hash is {sm.hash}")
        sm.author = m[1]
        sm.state = ReadyForDateState()


class IgnoringRecord():

    def __init__(self):
        self.blanks_seen = 0

    def feed(self, sm, line):
        sm.hash = ''
        if line.strip() == "":
            self.blanks_seen += 1
        if self.blanks_seen == 2:
            sm.state = ReadyState()


class ReadyForDateState:
    git_format = "%a %b %d %H:%M:%S %Y %z"

    def feed(self, sm: NumstatParser, line: str) -> None:
        if not line.startswith('Date:'):
            raise ParseError()
        _, date_part = line.split(':', 1)
        sm.date = datetime.strptime(date_part.strip(), self.git_format)
        sm.state = CollectingCommentState()


class CollectingCommentState:
    def __init__(self):
        self.collecting: Optional[str] = None

    def feed(self, sm: NumstatParser, line: str) -> None:
        if line == '':
            if self.collecting is None:
                return
            sm.comment = self.collecting
            sm.state = CollectingFileStatsState()
        elif line[0].isspace():
            usable = line.strip()
            self.collecting = (usable
                               if self.collecting is None
                               else "\n".join([self.collecting, usable])
                               )


class CollectingFileStatsState:
    pattern = re.compile(r"(?:\d+|-)\s+(?:\d+|-)\s+(.*)$")

    def __init__(self):
        self.collected = []

    def feed(self, sm: NumstatParser, line: str) -> None:
        if line == "":
            sm.filestats = self.collected
            sm.state = ReadyState()
            sm.can_emit = True
            return
        try:
            m = self.pattern.match(line)
            if not m:
                raise ParseError(f"File not in [{line}]")
            _, _, filename = line.split(maxsplit=2)
            self.collected.append(filename)
        except ValueError as err:
            raise ParseError(f'splitting [{line}] in 3s')
