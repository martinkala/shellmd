import sys
import argparse
from subprocess import Popen, TimeoutExpired, PIPE

ALLOWED_ACTIONS = ["execute", "dryrun", "parse", "parse_dir"]

class MDParser():
    START_MARKER = "#executable"
    RETURN_CODE_MARKER = "#executable expected return code"
    OUTPUT_MARKER = "#executable exact expected output is"
    OUTPUT_CONTAINS_MARKER = "#executable contains in expected output"

    @staticmethod
    def stripped(s):
        return s.lower().strip().replace(" ", "")

    def __init__(self):
        self.command_timout = 600

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

                    if line["has_validation"] is True:

                        # validtation for exact return code match
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
            is_executable = False

            # has validation is related to one line
            has_validation = False
            command = None

            # if executable marker is on begining of block
            if code_block[0].lower().strip() == MDParser.START_MARKER:
                is_executable = True

            started = False

            # iterate over all lines in code_block
            for line in code_block:

                # strip line to be able to comapre with markers
                stripped_line = MDParser.stripped(line)

                # if we hit validation parse and add to line

                if stripped_line[0:len(MDParser.stripped(MDParser.OUTPUT_MARKER))] == \
                        MDParser.stripped(MDParser.OUTPUT_MARKER):
                    command["validation"] = MDParser.analyze_condition(MDParser.OUTPUT_MARKER, line)
                    command["has_validation"] = True

                elif stripped_line[0:len(MDParser.stripped(MDParser.OUTPUT_CONTAINS_MARKER))] == \
                        MDParser.stripped(MDParser.OUTPUT_CONTAINS_MARKER):
                    command["validation"] = MDParser.analyze_condition(MDParser.OUTPUT_CONTAINS_MARKER, line)
                    command["has_validation"] = True

                elif stripped_line[0:len(MDParser.stripped(MDParser.RETURN_CODE_MARKER))] == \
                        MDParser.stripped(MDParser.RETURN_CODE_MARKER):
                    command["validation"] = MDParser.analyze_condition(MDParser.RETURN_CODE_MARKER, line)
                    command["has_validation"] = True

                elif stripped_line == MDParser.START_MARKER:
                    # just skip executable marker if found
                    pass

                else:
                    # if previous line was line of code
                    if started is True:
                        # then save previous line and start new line
                        analyzed_block.append(command)
                    else:
                        started = True

                    command = ({'command': line,
                                "has_validation": has_validation,
                                "is_executable": is_executable,
                                "validation": None})

            # save last command at the end of all lines in command
            if command is not None:
                analyzed_block.append(command)

            analyzed["blocks"].append(analyzed_block)

        return analyzed

    def parse_file(self, filename):
        """
        Method parses input md file for further processing
        :param filename: File to be parsed
        :return: parsed  - array of codeblocks where each code block contains lines from code block
        :throws: Invalid Code block
        """
        f = open(filename, "r")
        content = f.read()
        f.close()
        lines = content.split("\n")
        started = False
        code_blocks = []
        block = []

        # Iterate over all line
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
                    block.append(line)

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
        Method prety prints analyzed result
        :param analyzed:
        :return:
        """
        print("Analyzed")
        for block in analyzed['blocks']:
            for line in block:
                print(line)

    def execute_file(self, filename):
        """
        Method orchestrates file execution from parsing to os commands execution
        :param filename: string: path to file to be processed
        :return: None
        """
        parsed = self.parse_file(filename)
        analyzed = self.analyze_parsed(parsed)
        self.__execute_analyzed(analyzed)

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

    args = parser.parse_args()
    action = args.action
    input_file = args.input_file

    if action == "execute":
        mdp = MDParser()
        mdp.execute_file(input_file)

    if action == "parse":
        print(1)
        mdp = MDParser()
        parsed_output = mdp.parse_file(input_file)
        mdp.print_parsed(parsed_output)
        analyzed_output = mdp.analyze_parsed(parsed_output)
        mdp.print_analyzed(analyzed_output)
