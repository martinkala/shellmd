from unittest import TestCase, main
import sys
sys.path.insert(1, 'bin')
from shellmd import MDParser


class ParseTest(TestCase):

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
        self.assertEquals(len(parsed_array[0]), 2)
        self.assertEquals(parsed_array[0][0], "#executable")
        self.assertEquals(parsed_array[0][1], "ls -la")

    def test_parse_no_code_block(self):
        md_text = """
                #executable
                ls -la
        """

        md = MDParser()
        parsed_array = md.parse_md(md_text)
        print(parsed_array)
        self.assertEquals(len(parsed_array), 0)

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
        self.assertIn("blocks", analyzed.keys())
        self.assertEquals(len(analyzed["blocks"]), 1)
        self.assertIn("command", analyzed["blocks"][0][0].keys())

        com = analyzed["blocks"][0][0]
        for k in ParseTest.keys_to_check:
            self.assertIn(k, com.keys())
        self.assertEquals(com["command"], "ls -la")
        self.assertFalse(com["has_validation"])
        self.assertTrue(com["is_executable"])
        self.assertIsNone(com["validation"])

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
        self.assertIn("blocks", analyzed.keys())
        self.assertEquals(len(analyzed["blocks"]), 1)
        self.assertIn("command", analyzed["blocks"][0][0].keys())

        com = analyzed["blocks"][0][0]
        for k in ParseTest.keys_to_check:
            self.assertIn(k, com.keys())
        self.assertEquals(com["command"], "ls -la")
        self.assertFalse(com["has_validation"])
        self.assertTrue(com["is_executable"])
        self.assertIsNone(com["validation"])

        com = analyzed["blocks"][0][1]
        for k in ParseTest.keys_to_check:
            self.assertIn(k, com.keys())
        self.assertEquals(com["command"], "pwd")
        self.assertFalse(com["has_validation"])
        self.assertTrue(com["is_executable"])
        self.assertIsNone(com["validation"])

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

        self.assertIn("blocks", analyzed.keys())
        self.assertEquals(len(analyzed["blocks"]), 1)

        com = analyzed["blocks"][0][0]
        for k in ParseTest.keys_to_check:
            self.assertIn(k, com.keys())
        self.assertEquals(com["command"], "ls -la")
        self.assertFalse(com["has_validation"])
        self.assertFalse(com["is_executable"])
        self.assertIsNone(com["validation"])

        com = analyzed["blocks"][0][1]
        for k in ParseTest.keys_to_check:
            self.assertIn(k, com.keys())
        self.assertEquals(com["command"], "pwd")
        self.assertFalse(com["has_validation"])
        self.assertFalse(com["is_executable"])
        self.assertIsNone(com["validation"])

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

        self.assertIn("blocks", analyzed.keys())
        self.assertEquals(len(analyzed["blocks"]), 1)

        com = analyzed["blocks"][0][0]
        for k in ParseTest.keys_to_check:
            self.assertIn(k, com.keys())
        self.assertEquals(com["command"], "ls -la")

        self.assertFalse(com["has_validation"])
        self.assertTrue(com["is_executable"])
        self.assertIsNone(com["validation"])

        com = analyzed["blocks"][0][1]
        for k in ParseTest.keys_to_check:
            self.assertIn(k, com.keys())
        self.assertEquals(com["command"], "pwd")
        self.assertFalse(com["has_validation"])
        self.assertTrue(com["is_executable"])
        self.assertIsNone(com["validation"])

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

        self.assertIn("blocks", analyzed.keys())
        self.assertEquals(len(analyzed["blocks"]), 1)

        com = analyzed["blocks"][0][0]
        for k in ParseTest.keys_to_check:
            self.assertIn(k, com.keys())
        self.assertEquals(com["command"], "ls -la")

        self.assertFalse(com["has_validation"])
        self.assertFalse(com["is_executable"])
        self.assertIsNone(com["validation"])

        com = analyzed["blocks"][0][1]
        for k in ParseTest.keys_to_check:
            self.assertIn(k, com.keys())
        self.assertEquals(com["command"], "pwd")
        self.assertFalse(com["has_validation"])
        self.assertTrue(com["is_executable"])
        self.assertIsNone(com["validation"])

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

        self.assertIn("blocks", analyzed.keys())
        self.assertEquals(len(analyzed["blocks"]), 1)

        com = analyzed["blocks"][0][0]
        for k in ParseTest.keys_to_check:
            self.assertIn(k, com.keys())
        self.assertEquals(com["command"], "ls -la")
        self.assertFalse(com["has_validation"])
        self.assertTrue(com["is_executable"])
        self.assertIsNone(com["validation"])

        com = analyzed["blocks"][0][1]
        for k in ParseTest.keys_to_check:
            self.assertIn(k, com.keys())
        self.assertEquals(com["command"], "pwd")
        self.assertFalse(com["has_validation"])
        self.assertFalse(com["is_executable"])
        self.assertIsNone(com["validation"])

    def test_analyze_with_validation_return_code_0(self):
        """
        Test validation return code 0
        :return:
        """
        parsed = [['#executable',
                   'ls -la',
                   '#executable expected return code 0']]

        md = MDParser()
        analyzed = md.analyze_parsed(parsed)
        print(analyzed)

        self.assertIn("blocks", analyzed.keys())
        self.assertEquals(len(analyzed["blocks"]), 1)

        com = analyzed["blocks"][0][0]
        for k in ParseTest.keys_to_check:
            self.assertIn(k, com.keys())
        self.assertEquals(com["command"], "ls -la")
        self.assertTrue(com["has_validation"])
        self.assertTrue(com["is_executable"])
        self.assertIsNotNone(com["validation"])
        self.assertIn("type", com["validation"])
        self.assertEquals(com["validation"]["type"], MDParser.RETURN_CODE_MARKER)
        self.assertEquals(com["validation"]["value"], '0')

    def test_analyze_execute_with_validation_return_code_m1(self):
        """
        Test validation return code less than 0 on non existent command.
        Execute command and check if fails on assertion error


        :return:
        """
        md_content = """"
            ```
            #executable
            pwfg
            #executable expected return code 0
            ```
            """

        parsed = MDParser.parse_md(md_content)

        md = MDParser()
        analyzed = md.analyze_parsed(parsed)

        self.assertIn("blocks", analyzed.keys())
        self.assertEquals(len(analyzed["blocks"]), 1)

        com = analyzed["blocks"][0][0]
        for k in ParseTest.keys_to_check:
            self.assertIn(k, com.keys())
        self.assertEquals(com["command"], "pwfg")
        self.assertTrue(com["has_validation"])
        self.assertTrue(com["is_executable"])
        self.assertIsNotNone(com["validation"])
        self.assertIn("type", com["validation"])
        self.assertEquals(com["validation"]["type"], MDParser.RETURN_CODE_MARKER)
        self.assertEquals(com["validation"]["value"], '0')

        try:
            md.execute_md_string(md_content)
        except AssertionError as err:
            self.assertIsInstance(err, AssertionError)

    def test_analyze_execute_with_validation_output_contains(self):
        """
        Test validation command output contains ..

        :return:
        """
        md_content = """"
            ```
            #executable
            ls -la
            #executable contains in expected output ..
            ```
            """

        parsed = MDParser.parse_md(md_content)

        md = MDParser()
        analyzed = md.analyze_parsed(parsed)

        self.assertIn("blocks", analyzed.keys())
        self.assertEquals(len(analyzed["blocks"]), 1)

        com = analyzed["blocks"][0][0]
        for k in ParseTest.keys_to_check:
            self.assertIn(k, com.keys())
        self.assertEquals(com["command"], "ls -la")
        self.assertTrue(com["has_validation"])
        self.assertTrue(com["is_executable"])
        self.assertIsNotNone(com["validation"])
        self.assertIn("type", com["validation"])
        self.assertEquals(com["validation"]["type"], MDParser.OUTPUT_CONTAINS_MARKER)
        self.assertEquals(com["validation"]["value"], '..')

        md.execute_md_string(md_content)

    def test_analyze_execute_with_validation_exact_output(self):
        """
        Test validation command output contains ..

        :return:
        """
        md_content = """"
                ```
                #executable
                echo 1
                #executable exact expected output is 1
                ```
                """

        parsed = MDParser.parse_md(md_content)

        md = MDParser()
        analyzed = md.analyze_parsed(parsed)

        self.assertIn("blocks", analyzed.keys())
        self.assertEquals(len(analyzed["blocks"]), 1)

        com = analyzed["blocks"][0][0]
        for k in ParseTest.keys_to_check:
            self.assertIn(k, com.keys())
        self.assertEquals(com["command"], "echo 1")
        self.assertTrue(com["has_validation"])
        self.assertTrue(com["is_executable"])
        self.assertIsNotNone(com["validation"])
        self.assertIn("type", com["validation"])
        self.assertEquals(com["validation"]["type"], MDParser.OUTPUT_MARKER)
        self.assertEquals(com["validation"]["value"], '1')

        md.execute_md_string(md_content)


if __name__ == '__main__':
    main()