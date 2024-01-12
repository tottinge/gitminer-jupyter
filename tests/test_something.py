import unittest
from gminer import miner
from typer.testing import CliRunner

from gminer.miner import app

runner = CliRunner()


class MyTestCase(unittest.TestCase):
    def test_all_commands_present(self):
        result = runner.invoke(app, '--help')
        self.assertEqual(0, result.exit_code)
        commands = [
            'commits-per-day',
            'extract-to-json',
            'most-committed',
            'strongest-pairs',
            'tightest-groupings'
        ]
        for command in commands:
            with self.subTest(command):
                self.assertIn(command, result.output)


if __name__ == '__main__':
    unittest.main()
