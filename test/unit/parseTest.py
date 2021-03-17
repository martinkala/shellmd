import unittest
import sys
sys.path.insert(1, 'bin')
from shellmd import MDParser


class ParseTest(unittest.TestCase):

    keys_to_check = ["validation", "is_executable", "command", "has_validation"]

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

        com = analyzed["blocks"][0][0]
        for k in ParseTest.keys_to_check:
            assert k in com.keys(), "Expected key %s" % k
        assert com["command"] == "ls -la", "Expected command pwd Actual: %s" % com["command"]
        assert com["has_validation"] is False, "Expected has_validation False Actual: %s" % com["has_validation"]
        assert com["is_executable"] is True, "Expected is_executable False Actual: %s" % com["is_executable"]
        assert com["validation"] is None, "Expected validation None Actual: %s" % com["validation"]

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

        com = analyzed["blocks"][0][0]
        for k in ParseTest.keys_to_check:
            assert k in com.keys(), "Expected key %s" % k
        assert com["command"] == "ls -la", "Expected command pwd Actual: %s" % com["command"]
        assert com["has_validation"] is False, "Expected has_validation False Actual: %s" % com["has_validation"]
        assert com["is_executable"] is True, "Expected is_executable False Actual: %s" % com["is_executable"]
        assert com["validation"] is None, "Expected validation None Actual: %s" % com["validation"]

        com = analyzed["blocks"][0][1]
        for k in ParseTest.keys_to_check:
            assert k in com.keys(), "Expected key %s" % k
        assert com["command"] == "pwd", "Expected command pwd Actual: %s" % com["command"]
        assert com["has_validation"] is False, "Expected has_validation False Actual: %s" % com["has_validation"]
        assert com["is_executable"] is True, "Expected is_executable False Actual: %s" % com["is_executable"]
        assert com["validation"] is None, "Expected validation None Actual: %s" % com["validation"]

    def test_analyze_without_control(self):
        """
        Test two_lines without control commands executable or validation
        Expectetation, no command will be executable
        :return:
        """
        parsed = [['ls -la',
                   'pwd']]
        md = MDParser()
        analyzed = md.analyze_parsed(parsed)
        print("a")
        print(analyzed)

        assert "blocks" in analyzed.keys() , "Expected block key exist"
        assert len(analyzed["blocks"]) == 1, "Expected num blocks 1 Actual:%s" % len(analyzed["blocks"])

        com = analyzed["blocks"][0][0]
        for k in ParseTest.keys_to_check:
            assert k in com.keys(), "Expected key %s" % k
        assert com["command"] == "ls -la", "Expected command ls -la  Actual: %s" % com["command"]
        assert com["has_validation"] is False, "Expected has_validation False Actual: %s" % com["has_validation"]
        assert com["is_executable"] is False, "Expected is_executable False Actual: %s" % com["is_executable"]
        assert com["validation"] is None, "Expected validation None Actual: %s" % com["validation"]

        com = analyzed["blocks"][0][1]
        for k in ParseTest.keys_to_check:
            assert k in com.keys(), "Expected key %s" % k
        assert com["command"] == "pwd", "Expected command pwd Actual: %s" % com["command"]
        assert com["has_validation"] is False, "Expected has_validation False Actual: %s" % com["has_validation"]
        assert com["is_executable"] is False, "Expected is_executable False Actual: %s" % com["is_executable"]
        assert com["validation"] is None, "Expected validation None Actual: %s" % com["validation"]

    def test_analyze_without_control_with_all_executables(self):
        """
        Test two_lines without control commands executable or validation, but with overidden all_executables
        Expectetation, all commands will be executable
        :return:
        """
        parsed = [['ls -la',
                   'pwd']]
        md = MDParser(all_executable=True)
        analyzed = md.analyze_parsed(parsed)
        print("a")
        print(analyzed)

        assert "blocks" in analyzed.keys() , "Expected block key exist"
        assert len(analyzed["blocks"]) == 1, "Expected num blocks 1 Actual:%s" % len(analyzed["blocks"])

        com = analyzed["blocks"][0][0]
        for k in ParseTest.keys_to_check:
            assert k in com.keys(), "Expected key %s" % k
        assert com["command"] == "ls -la", "Expected command ls -la  Actual: %s" % com["command"]
        assert com["has_validation"] is False, "Expected has_validation False Actual: %s" % com["has_validation"]
        assert com["is_executable"] is True, "Expected is_executable False Actual: %s" % com["is_executable"]
        assert com["validation"] is None, "Expected validation None Actual: %s" % com["validation"]

        com = analyzed["blocks"][0][1]
        for k in ParseTest.keys_to_check:
            assert k in com.keys(), "Expected key %s" % k
        assert com["command"] == "pwd", "Expected command pwd Actual: %s" % com["command"]
        assert com["has_validation"] is False, "Expected has_validation False Actual: %s" % com["has_validation"]
        assert com["is_executable"] is True, "Expected is_executable False Actual: %s" % com["is_executable"]
        assert com["validation"] is None, "Expected validation None Actual: %s" % com["validation"]

    def test_analyze_with_control_in_the_middle(self):
        """
        Test two_lines without control #executable after first command
        Expectetation, first command will be not be executable , second command will be executable
        :return:
        """
        parsed = [['ls -la',
                   '#executable',
                   'pwd']]

        md = MDParser()
        analyzed = md.analyze_parsed(parsed)
        print(analyzed)

        assert "blocks" in analyzed.keys() , "Expected block key exist"
        assert len(analyzed["blocks"]) == 1, "Expected num blocks 1 Actual:%s" % len(analyzed["blocks"])

        com = analyzed["blocks"][0][0]
        for k in ParseTest.keys_to_check:
            assert k in com.keys(), "Expected key %s" % k
        assert com["command"] == "ls -la", "Expected command ls -la  Actual: %s" % com["command"]
        assert com["has_validation"] is False, "Expected has_validation False Actual: %s" % com["has_validation"]
        assert com["is_executable"] is False, "Expected is_executable False Actual: %s" % com["is_executable"]
        assert com["validation"] is None, "Expected validation None Actual: %s" % com["validation"]

        com = analyzed["blocks"][0][1]
        for k in ParseTest.keys_to_check:
            assert k in com.keys(), "Expected key %s" % k
        assert com["command"] == "pwd", "Expected command pwd Actual: %s" % com["command"]
        assert com["has_validation"] is False, "Expected has_validation False Actual: %s" % com["has_validation"]
        assert com["is_executable"] is True, "Expected is_executable True Actual: %s" % com["is_executable"]
        assert com["validation"] is None, "Expected validation None Actual: %s" % com["validation"]

    def test_analyze_with_stop_executable(self):
        """
        Test two_lines without control #executable after first command
        Expectetation, first command will be not be executable , second command will be executable
        :return:
        """
        parsed = [['#executable',
                   'ls -la',
                   '#executable stop',
                   'pwd']]

        md = MDParser()
        analyzed = md.analyze_parsed(parsed)
        print(analyzed)

        assert "blocks" in analyzed.keys() , "Expected block key exist"
        assert len(analyzed["blocks"]) == 1, "Expected num blocks 1 Actual:%s" % len(analyzed["blocks"])

        com = analyzed["blocks"][0][0]
        for k in ParseTest.keys_to_check:
            assert k in com.keys(), "Expected key %s" % k
        assert com["command"] == "ls -la", "Expected command ls -la  Actual: %s" % com["command"]
        assert com["has_validation"] is False, "Expected has_validation False Actual: %s" % com["has_validation"]
        assert com["is_executable"] is True, "Expected is_executable True Actual: %s" % com["is_executable"]
        assert com["validation"] is None, "Expected validation None Actual: %s" % com["validation"]

        com = analyzed["blocks"][0][1]
        for k in ParseTest.keys_to_check:
            assert k in com.keys(), "Expected key %s" % k
        assert com["command"] == "pwd", "Expected command pwd Actual: %s" % com["command"]
        assert com["has_validation"] is False, "Expected has_validation False Actual: %s" % com["has_validation"]
        assert com["is_executable"] is False, "Expected is_executable False Actual: %s" % com["is_executable"]
        assert com["validation"] is None, "Expected validation None Actual: %s" % com["validation"]
if __name__ == '__main__':
    unittest.main()