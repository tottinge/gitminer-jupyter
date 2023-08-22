import unittest

from numstat_parser import ReadyState, ReadyForAuthor, ReadyForDateState, CollectingCommentState, \
    CollectingFileStatsState, NumstatParser, ParseError


class InReadyState(unittest.TestCase):
    def setUp(self):
        self.p = NumstatParser()

    def test_empty_line_ignored(self):
        p = self.p
        p.feed("")
        assert p.has_record() is False

    def test_commit_line_recognized(self):
        p = self.p
        p.feed("commit df263690d1acae6d2b587e2c9c51fcbb9b24e036")
        assert p.hash == "df263690d1acae6d2b587e2c9c51fcbb9b24e036"
        assert isinstance(p.state, ReadyForAuthor)

    def test_other_content_rejected(self):
        p = self.p
        with self.assertRaises(ParseError):
            p.feed("any other text")
        assert isinstance(p.state, ReadyState)


class InAuthorState(unittest.TestCase):
    def setUp(self):
        self.parser = NumstatParser()
        self.parser.state = ReadyForAuthor()

    def test_receives_author_string(self):
        self.parser.feed("Author: Me <me@example.com>\n")
        self.assertEqual(self.parser.author, "me@example.com")

    def test_other_text_rejected(self):
        with self.assertRaises(ParseError):
            self.parser.feed("not an author line")


class InParseState(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = NumstatParser()
        self.parser.state = ReadyForDateState()

    def test_rejects_non_date(self):
        with self.assertRaises(ParseError):
            self.parser.feed("not the date line")

    def test_receives_date_line(self):
        p = self.parser
        p.feed("Date:   Mon Jun 12 13:00:12 2023 +0200")
        self.assertEquals(p.date.year, 2023)
        self.assertEquals(p.date.month, 6)
        self.assertEquals(p.date.hour, 13)
        self.assertIsInstance(p.state, CollectingCommentState)


class InCollectingCommentState(unittest.TestCase):
    def setUp(self) -> None:
        parser = NumstatParser()
        parser.state = CollectingCommentState()
        self.parser = parser

    def test_accepts_initial_blank_line(self):
        self.parser.feed("")
        self.assertIsInstance(self.parser.state, CollectingCommentState)

    def test_accepts_one_line_comment(self):
        comment = "     this is a comment"
        self.parser.feed(comment)
        self.parser.feed("")
        self.assertEqual(self.parser.comment, comment.strip())

    def test_accept_multiline_comment(self):
        comments = [
            "    this is a comment",
            "    feat: Changes relates to implementing a user store in Mongo",
            "    test: wrapped test around code like a warm python"
        ]
        for comment in comments:
            self.parser.feed(comment)

        expected = "\n".join(s.strip() for s in comments)
        self.parser.feed("")
        self.assertEqual(self.parser.comment, expected)
        self.assertIsInstance(self.parser.state, CollectingFileStatsState)


class InCollectingFileState(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = NumstatParser()
        self.parser.state = CollectingFileStatsState()

    def test_invalid_line_raises_exception(self):
        with self.assertRaises(ParseError):
            self.parser.feed("This isn't right at all")

    def test_blank_line_terminates_empty_group(self):
        parser = self.parser
        parser.feed("")
        self.assertIsInstance(parser.state, ReadyState)
        self.assertEqual(parser.filestats, [])
        self.assertIsInstance(parser.state, ReadyState)

    def test_accepts_one_filestat(self):
        parser = self.parser
        parser.feed("50	64	main.py")
        parser.feed("")
        self.assertEqual(["main.py"], parser.filestats)

    def test_accepts_multiple_filestat(self):
        parser = self.parser
        lines = [
            "7    0    pre-commit.yaml",
            "2    0    devtools.txt",
            "49   0    precommit.md",
            "0    9    test_delme.py"
        ]
        for line in lines:
            parser.feed(line)
        parser.feed("")

        expected = [
            "pre-commit.yaml",
            "devtools.txt",
            "precommit.md",
            "test_delme.py"
        ]
        self.assertEquals(expected, self.parser.filestats)

    def test_accepts_binary_file_update(self):
        parser = self.parser
        parser.feed("-    -    binary.file")
        parser.feed('')
        self.assertEqual(['binary.file'], parser.filestats)


class RecordHandling(unittest.TestCase):
    def test_reads_one_record_with_file_content(self):
        parser = NumstatParser()
        for line in (
'''commit 8e0d5ec0e23ca9684cff95e204e682cbe9386231
Author: Tim Ottinger <tottinge@industriallogic.com>
Date:   Mon Jun 12 16:09:43 2023 +0200

    doc: improve the precommit.md

9	1	precommit.md

''').split('\n'):
            parser.feed(line)
        expected = ['precommit.md']
        actual = parser.filestats
        self.assertListEqual(expected, actual)
        self.assertTrue(parser.can_emit)
        commit = parser.emit()

if __name__ == '__main__':
    unittest.main()
