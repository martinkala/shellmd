import unittest
import sys
sys.path.insert(1, 'bin')
from shellmd import MDParser


class ParseTest(unittest.TestCase):

    def test_parse(self):
        md_text = """
            ```
                #executable
                ls -la
            ```
        """

        md = MDParser()
        parsed_array = md.parse_md(md_text)
        print(parsed_array)
        assert len(parsed_array[0]) == 2, "Expected number of nodes is 2 , Actual %s" % len(parsed_array)
        assert parsed_array[0][0] == "#executable", "Actual %s" % parsed_array[0][0]
        assert parsed_array[0][1] == "ls -la", "Actual %s" % parsed_array[0][1]

    def test_analyze_simple_line(self):
        """
        Test one line with executable no validation
        :return:
        """
        parsed = [['#executable',
                    'ls -la']]

        md = MDParser()
        analyzed = md.analyze_parsed(parsed)
        print(analyzed)
        assert "blocks" in analyzed.keys() , "Expected block key exist"
        assert len(analyzed["blocks"]) == 1, "Expected num blocks 1 Actual:%s" % len(analyzed["blocks"])
        assert "command" in analyzed["blocks"][0][0].keys(), "Expected key command"
        assert analyzed["blocks"][0][0]["command"] == "ls -la", \
            "Expected command ls -la  Actual: %s" % analyzed["blocks"][0][0]["command"]
        assert "has_validation" in analyzed["blocks"][0][0].keys(), "Expected key has_validation"
        assert analyzed["blocks"][0][0]["has_validation"] is False, \
            "Expected has_validation False Actual: %s" % analyzed["blocks"][0][0]["has_validation"]
        assert "is_executable" in analyzed["blocks"][0][0].keys(), "Expected key is_executable"
        assert analyzed["blocks"][0][0]["is_executable"] is True, \
            "Expected is_executable True Actual: %s" % analyzed["blocks"][0][0]["is_executable"]
        assert "validation" in analyzed["blocks"][0][0].keys(), "Expected key validation"
        assert analyzed["blocks"][0][0]["validation"] is None, \
            "Expected validation None Actual: %s" % analyzed["blocks"][0][0]["validation"]

    def test_analyze_two_lines(self):
        """
        Test two_lines with executable no validation
        :return:
        """
        parsed = [['#executable',
                   'ls -la',
                   'pwd']]

        md = MDParser()
        analyzed = md.analyze_parsed(parsed)
        print(analyzed)
        assert "blocks" in analyzed.keys() , "Expected block key exist"
        assert len(analyzed["blocks"]) == 1, "Expected num blocks 1 Actual:%s" % len(analyzed["blocks"])
        assert "command" in analyzed["blocks"][0][0].keys(), "Expected key command"

        assert analyzed["blocks"][0][0]["command"] == "ls -la", \
            "Expected command ls -la  Actual: %s" % analyzed["blocks"][0][0]["command"]
        assert "has_validation" in analyzed["blocks"][0][0].keys(), "Expected key has_validation"
        assert analyzed["blocks"][0][0]["has_validation"] is False, \
            "Expected has_validation False Actual: %s" % analyzed["blocks"][0][0]["has_validation"]
        assert "is_executable" in analyzed["blocks"][0][0].keys(), "Expected key is_executable"
        assert analyzed["blocks"][0][0]["is_executable"] is True, \
            "Expected is_executable True Actual: %s" % analyzed["blocks"][0][0]["is_executable"]
        assert "validation" in analyzed["blocks"][0][0].keys(), "Expected key validation"
        assert analyzed["blocks"][0][0]["validation"] is None, \
            "Expected validation None Actual: %s" % analyzed["blocks"][0][0]["validation"]

        assert analyzed["blocks"][0][1]["command"] == "pwd", \
            "Expected command pwd Actual: %s" % analyzed["blocks"][0][1]["command"]
        assert "has_validation" in analyzed["blocks"][0][1].keys(), "Expected key has_validation"
        assert analyzed["blocks"][0][1]["has_validation"] is False, \
            "Expected has_validation False Actual: %s" % analyzed["blocks"][0][1]["has_validation"]
        assert "is_executable" in analyzed["blocks"][0][1].keys(), "Expected key is_executable"
        assert analyzed["blocks"][0][1]["is_executable"] is True, \
            "Expected is_executable True Actual: %s" % analyzed["blocks"][0][1]["is_executable"]
        assert "validation" in analyzed["blocks"][0][1].keys(), "Expected key validation"
        assert analyzed["blocks"][0][1]["validation"] is None, \
            "Expected validation None Actual: %s" % analyzed["blocks"][0][1]["validation"]


if __name__ == '__main__':
    unittest.main()