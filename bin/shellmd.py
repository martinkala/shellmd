import sys
import argparse
from subprocess import Popen, TimeoutExpired, PIPE

ALLOWED_ACTIONS = ["execute", "dryrun", "parse", "parse_dir"]


class MDParser():
    """
    Class handles parsing analyzing and executing for block of codes in input files.
    """
    START_MARKER = "#executable block"
    STOP_MARKER = "#executable stop"
    RETURN_CODE_MARKER = "#executable expected return code"
    OUTPUT_MARKER = "#executable exact expected output is"
    OUTPUT_CONTAINS_MARKER = "#executable contains in expected output"
    TAG_MARKER = "#executable tag"

    @staticmethod
    def stripped(s):
        return s.lower().strip().replace(" ", "")

    def __init__(self, all_executable=False, command_timeout=600):
        self.command_timout = command_timeout
        self.all_executable = all_executable

    def __execute_analyzed(self, analyzed):
        command_cnt = 0
        block_cnt = 0
        for code_block in analyzed["blocks"]:

            for line in code_block:
                if line["is_executable"] is True:
                    command = line['command']
                    print("-----------------------")
                    print(command)
                    p = Popen(command, shell=True, stdout=PIPE)

                    try:
                        outs, errs = p.communicate(timeout=self.command_timout)
                        outs = outs.decode("utf-8").strip()
                        ret_code = p.returncode

                    except TimeoutExpired:
                        p.kill()
                        outs, errs = p.communicate()
                        ret_code = p.returncode

                    if line["validation"] is not None:

                        # validation for exact return code match
                        if line["validation"]["type"] == MDParser.RETURN_CODE_MARKER:
                            assert str(ret_code) == line["validation"]["value"], \
                                "Validation %s fails on value check. Expected |%s| Actual |%s|" \
                                % (line["validation"]["type"], line["validation"]["value"], ret_code)

                        # validation for exact std output match
                        if line["validation"]["type"] == MDParser.OUTPUT_MARKER:
                            assert outs == line["validation"]["value"], \
                                "Validation %s fails on std output check. Expected |%s| Actual |%s|" \
                                % (line["validation"]["type"], line["validation"]["value"], outs)

                        # validation for output contains substring
                        if line["validation"]["type"] == MDParser.OUTPUT_CONTAINS_MARKER:
                            assert outs.find(line["validation"]["value"]) > -1, \
                                "Validation %s fails on std out contains check check. Searching %s Actual %s" \
                                % (line["validation"]["type"], line["validation"]["value"], outs)

                    else:
                        assert ret_code == 0,\
                            "Default return code for command |%s| fails on value check. Expected:0 Actual:%s" \
                            % (line['command'], ret_code)
                    command_cnt += 1
            block_cnt += 1

        print("Succesfully executed %s commands in %s blocks" % (command_cnt, block_cnt))

    def analyze_parsed(self, parsed):
        """
        Method analyses parsed code block for executable markers and tags
        :param parsed: array of codeblocks where each code block contains lines from code block
        return transformed array
        """
        analyzed = {'blocks': []}
        for code_block in parsed:
            analyzed_block = []

            # executable is related to whole block
            # if executable flag is overridden for whole parser
            if self.all_executable is True:
                # then each line will be set to executable by default
                is_executable = True
            else:
                is_executable = False

            # New command preparation
            command = ({'command': "",
                        "is_executable": is_executable,
                        "validation": None})

            # iterate over all lines in code_block
            for line in code_block:

                # strip line to be able to compare with markers
                stripped_line = MDParser.stripped(line)

                # if we hit validation parse and add to line

                if stripped_line[0:len(MDParser.stripped(MDParser.OUTPUT_MARKER))] == \
                        MDParser.stripped(MDParser.OUTPUT_MARKER):
                    command["is_executable"] = True
                    command["validation"] = MDParser.analyze_condition(MDParser.OUTPUT_MARKER, line)

                elif stripped_line[0:len(MDParser.stripped(MDParser.OUTPUT_CONTAINS_MARKER))] == \
                        MDParser.stripped(MDParser.OUTPUT_CONTAINS_MARKER):
                    command["is_executable"] = True
                    command["validation"] = MDParser.analyze_condition(MDParser.OUTPUT_CONTAINS_MARKER, line)

                elif stripped_line[0:len(MDParser.stripped(MDParser.RETURN_CODE_MARKER))] == \
                        MDParser.stripped(MDParser.RETURN_CODE_MARKER):
                    command["is_executable"] = True
                    command["validation"] = MDParser.analyze_condition(MDParser.RETURN_CODE_MARKER, line)

                elif stripped_line == MDParser.stripped(MDParser.START_MARKER):
                    # from now all commands are executable
                    is_executable = True
                    command["is_executable"] = is_executable
                    command["validation"] = None

                elif stripped_line[0:len(MDParser.stripped(MDParser.TAG_MARKER))] == \
                        MDParser.stripped(MDParser.TAG_MARKER):
                    # Add tag to command
                    pass

                elif stripped_line == MDParser.stripped(MDParser.STOP_MARKER):
                    # from now all commands are not executable , only when overridden with all_executable
                    if self.all_executable is False:
                        is_executable = False
                        command["is_executable"] = is_executable

                else:
                    # then save command together with
                    command["command"] = line
                    analyzed_block.append(command)

                    # New command preparation
                    command = ({'command': "",
                                "is_executable": is_executable,
                                "validation": None})

            analyzed["blocks"].append(analyzed_block)

        return analyzed

    @staticmethod
    def read_file(filename):
        """
        Read input md file
        :param filename: File to be parsed
        :return: file content as text
        """

        f = open(filename, "r")
        content = f.read()
        f.close()
        return content

    @staticmethod
    def parse_md(md_content):
        """
        Method parses input md text for further processing
        :param md_content: content with md markdown to be processed
        :return: parsed  - array of codeblocks where each code block contains lines from code block
        :throws: Invalid Code block
        """
        lines = md_content.split("\n")
        started = False
        code_blocks = []
        block = []

        # Iterate over all lines
        for line in lines:
            if line.strip() == "```":
                if started is True:
                    # second block mark when processing blog finishes filling of block
                    started = False
                    code_blocks.append(block)
                    block = []
                else:
                    started = True
            else:
                if started is True:
                    block.append(line.strip())

        # Invalid document with even code block markers
        if started is True:
            print("Invalid code block - Block not finished")
            print(block)
            sys.exit(2)
        return code_blocks

    @staticmethod
    def print_parsed(parsed):
        """
        Method pretty prints Parsing result
        :param parsed: parsed structure
        :return: NOne
        """
        print("Parsed")
        for line in parsed:
            print(line)

    @staticmethod
    def print_analyzed(analyzed):
        """
        Method pretty prints analyzed result
        :param analyzed:
        :return:
        """
        print("Analyzed")
        for block in analyzed['blocks']:
            for line in block:
                print(line)

    def execute_md_string(self, md_content):
        """
        Method executes md string
        :param analyzed:
        :return:
        """

        parsed = MDParser.parse_md(md_content)
        analyzed = self.analyze_parsed(parsed)
        self.__execute_analyzed(analyzed)

    def execute_file(self, filename):
        """
        Method orchestrates file execution from parsing to os commands execution
        :param filename: string: path to file to be processed
        :return: None
        """
        md_content = MDParser.read_file(filename)
        self.execute_md_string(md_content)

    @staticmethod
    def analyze_condition(validation_type, line):
        """
        Mathod analyzes validation oneliner and create validation dict with validation type and value to be used in
        validation execution
        """
        value = line.split(validation_type)[1].strip()

        validation = {"type": validation_type, "value": value}

        return validation


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process md files as executable files')

    parser.add_argument('--action',
                        required=False,
                        default="execute",
                        choices=ALLOWED_ACTIONS,
                        help='Action to be executed')

    parser.add_argument('--input-file',
                        default=None,
                        required=True,
                        help='Input file / files  to be processed')

    parser.add_argument('--all-executable',
                        default="No",
                        required=False,
                        choices=["yes", "no"],
                        help='If all lines except are executable')

    args = parser.parse_args()
    action = args.action
    input_file = args.input_file
    all_executable = args.all_executable

    if all_executable == "yes":
        all_executable = True
    else:
        all_executable = True

    if action == "execute":
        mdp = MDParser(all_executable=all_executable)
        mdp.execute_file(input_file)

    if action == "parse":
        print(1)
        mdp = MDParser()
        content = MDParser.read_file(input_file)
        parsed_output = MDParser.parse_md(content)
        mdp.print_parsed(parsed_output)
        analyzed_output = mdp.analyze_parsed(parsed_output)
        mdp.print_analyzed(analyzed_output)
