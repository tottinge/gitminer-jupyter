import unittest
from datetime import date
from textwrap import dedent

from numstat_parser import ReadyState, ReadyForAuthor, ReadyForDateState, CollectingCommentState, \
    CollectingFileStatsState, NumstatParser, ParseError, read_all_commits, IgnoringRecord


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


class InIgnoreState(unittest.TestCase):
    def test_ignoring_just_enough(self):
        parser = NumstatParser()
        parser.state = IgnoringRecord()
        parser.feed("nonsense")
        parser.feed("     first empty follows")
        parser.feed("")
        parser.feed("second empty follows")
        parser.feed("")
        self.assertIsInstance(parser.state, ReadyState)


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

    def test_accepts_multiline_with_blanks(self):
        comments = [
            "    this is the first line with an empty line following",
            "    ",
            "    feat: Changes relates to implementing a user store in Mongo",
            "    ",
            "    ",
            "    test: wrapped test around code like a warm python",
            ""
        ]
        for comment in comments:
            self.parser.feed(comment)
        self.assertIn('the first', self.parser.comment)
        self.assertIn('warm python', self.parser.comment)
        self.assertIsInstance(self.parser.state, CollectingFileStatsState, f"Got {self.parser.state}")


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


three_records = """

commit df263690d1acae6d2b587e2c9c51fcbb9b24e036
Author: Perry Reid <wpreid@gmail.com>
Date:   Tue Jun 13 10:00:18 2023 -0500

    Updated to the latest chromedriver

-	-	webdrivers/darwin/chromedriver

commit 8e0d5ec0e23ca9684cff95e204e682cbe9386231
Author: Tim Ottinger <tottinge@industriallogic.com>
Date:   Mon Jun 12 16:09:43 2023 +0200

    doc: improve the precommit.md

9	1	precommit.md

commit 189ec9b8ebf9806d3d16c3b1c55f5ccf3874eb9c
Author: Tim Ottinger <tottinge@industriallogic.com>
Date:   Mon Jun 12 16:05:02 2023 +0200

    chore: got precommit hooks using black & bandit

7	0	.pre-commit-config.yaml
2	0	devtools.txt
49	0	precommit.md
0	9	test_delme.py

"""


class RecordHandling(unittest.TestCase):

    def test_ignores_merge_records(self):
        parser = NumstatParser()
        for line in dedent('''
            commit c689dff744d8673640e3efeaed530374ef4c0bc3
            Merge: fae63c71 7f627b50
            Author: Cecil Williams <cecil.g.williams@gmail.com>
            Date:   Wed Jul 26 12:48:20 2023 -0500
            
                Merge branch 'contact-page'
            
        ''').split('\n'):
            parser.feed(line)
        self.assertIsInstance(parser.state, ReadyState)

    def test_reads_one_record_with_file_content(self):
        parser = NumstatParser()
        for line in (dedent('''
                    commit 8e0d5ec0e23ca9684cff95e204e682cbe9386231
                    Author: Tim Ottinger <tottinge@industriallogic.com>
                    Date:   Mon Jun 12 16:09:43 2023 +0200
                    
                        doc: improve the precommit.md
                    
                    9	1	precommit.md
                ''')).split('\n'):
            parser.feed(line)
        self.assertTrue(parser.can_emit)
        commit, files = parser.emit()
        self.assertEqual('8e0d5ec0e23ca9684cff95e204e682cbe9386231', commit.hash)
        self.assertEqual('doc: improve the precommit.md', commit.message)
        record_date = date(2023, 6, 12)
        self.assertEqual(record_date, commit.timestamp.date())
        self.assertEqual(['precommit.md'], files)

    def test_series_of_records(self):
        output = [record for record in read_all_commits(three_records.split('\n'))]
        records = [record for (record, _) in output]
        filelist = [files for (_, files) in output]
        self.assertEqual(3, len(records))
        self.assertEqual([1, 1, 4], [len(x) for x in filelist])


if __name__ == '__main__':
    unittest.main()
