import os
import sys
import argparse
from subprocess import Popen, TimeoutExpired, PIPE

ALLOWED_ACTIONS = ["execute", "dryrun", "parse", "parse_dir"]

class MDParser():
    """
    Class handles parsing analyzing and executing for block of codes in input files.
    """
    START_MARKER = "#executable block"
    STOP_MARKER = "#executable block end"
    RETURN_CODE_MARKER = "#executable expected return code"
    OUTPUT_MARKER = "#executable exact expected output is"
    OUTPUT_CONTAINS_MARKER = "#executable contains in expected output"
    TAG_MARKER = "#executable tag"

    @staticmethod
    def stripped(s):
        return s.strip().replace(" ", "")

    @staticmethod
    def stripped_lowered(s):
        return s.lower().strip().replace(" ", "")

    def __init__(self, all_executable=False, command_timeout=600, intend=2, output_file=None, debug_env_vars=None):
        self.command_timout = command_timeout
        self.all_executable = all_executable
        self.intend = int(intend)
        self.output_file = output_file
        self.debug_env_vars = debug_env_vars

        if debug_env_vars is not None:
            self.debug_env_vars = debug_env_vars.split(",")

    def append_to_out_file(self, command, outs, errs, ret_code, vars_to_print=None):
        """
        Method writes basic command info into output file for further investigation
        :param command: executed command
        :param outs: standard output
        :param errs: standard error
        :param ret_code: command return code

        """
        out_f = open(self.output_file,"a+")

        output_string = "command: %s\n" %command
        output_string += "return code: %s\n" % errs
        output_string += "stderr: %s\n" % ret_code
        if vars_to_print is not None:
            output_string += "debug_vars: %s\n" % vars_to_print
        output_string += "stdout: %s\n" % (outs)

        out_f.write(output_string+"\n")

        out_f.close()

    def __execute_analyzed(self, analyzed, config_vars):
        command_cnt = 0
        block_cnt = 0

        # append variable from config_vars to environment vars
        # variables form config file overrides current environment variable
        for k in config_vars.keys():
            os.environ[k] = config_vars[k]
        i = 0

        vars_to_print = []
        if self.debug_env_vars is not None:
            for k in os.environ.keys():
                if k in self.debug_env_vars:
                    vars_to_print.append("%s=%s" % (k,os.environ[k]))

        for code_block in analyzed["blocks"]:
            i+=1
            print("".rjust(self.intend*2)+"Processing codeblock no. %s" % i)
            print("".rjust(self.intend*3)+"--------------------------")
            for line in code_block:
                if line["is_executable"] is True:
                    command = line['command']
                    print("".ljust(self.intend*4)+command)
                    p = Popen(command, shell=True, stdout=PIPE)

                    try:
                        outs, errs = p.communicate(timeout=self.command_timout)
                        outs = outs.decode("utf-8").strip()
                        ret_code = p.returncode
                        if self.output_file is not None:
                            self.append_to_out_file(command, outs, errs, ret_code, vars_to_print)

                    except TimeoutExpired:
                        p.kill()
                        outs, errs = p.communicate()
                        ret_code = p.returncode
                        if self.output_file is not None:
                            self.append_to_out_file(command, outs, errs, ret_code, vars_to_print)

                    if line["validation"] is not None:
                        print(line['validation'])
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
            print("".rjust(self.intend*3)+"--------------------------")
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
                stripped_lowered_line = MDParser.stripped_lowered(line)

                # if we hit validation parse and add to line
                if stripped_lowered_line == MDParser.stripped_lowered(MDParser.STOP_MARKER):
                    # from now all commands are not executable , only when overridden with all_executable
                    if self.all_executable is False:
                        is_executable = False
                        command["is_executable"] = is_executable

                elif stripped_lowered_line[0:len(MDParser.stripped_lowered(MDParser.OUTPUT_MARKER))] == \
                        MDParser.stripped_lowered(MDParser.OUTPUT_MARKER):
                    command["is_executable"] = True
                    command["validation"] = MDParser.analyze_condition(MDParser.OUTPUT_MARKER, line)

                elif stripped_lowered_line[0:len(MDParser.stripped_lowered(MDParser.OUTPUT_CONTAINS_MARKER))] == \
                        MDParser.stripped_lowered(MDParser.OUTPUT_CONTAINS_MARKER):
                    command["is_executable"] = True
                    command["validation"] = MDParser.analyze_condition(MDParser.OUTPUT_CONTAINS_MARKER, line)

                elif stripped_lowered_line[0:len(MDParser.stripped_lowered(MDParser.RETURN_CODE_MARKER))] == \
                        MDParser.stripped_lowered(MDParser.RETURN_CODE_MARKER):
                    command["is_executable"] = True
                    command["validation"] = MDParser.analyze_condition(MDParser.RETURN_CODE_MARKER, line)

                elif stripped_lowered_line == MDParser.stripped_lowered(MDParser.START_MARKER):
                    # from now all commands are executable
                    is_executable = True
                    command["is_executable"] = is_executable
                    command["validation"] = None

                elif stripped_lowered_line[0:len(MDParser.stripped_lowered(MDParser.TAG_MARKER))] == \
                        MDParser.stripped_lowered(MDParser.TAG_MARKER):
                    # Add tag to command
                    pass

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

    def execute_md_string(self, md_content, config_vars):
        """
        Method executes md string
        :param md_content:
        :param config_vars:
        :return:
        """

        parsed = MDParser.parse_md(md_content)
        analyzed = self.analyze_parsed(parsed)
        self.__execute_analyzed(analyzed, config_vars)

    def execute_file(self, filename, config_vars={}):
        """
        Method orchestrates file execution from parsing to os commands execution
        :param filename: string: path to file to be processed
        :param config_vars: dict: environment variables to inject
        :return: None
        """
        md_content = MDParser.read_file(filename)
        self.execute_md_string(md_content, config_vars)

    @staticmethod
    def analyze_condition(validation_type, line):
        """
        Mathod analyzes validation oneliner and create validation dict with validation type and value to be used in
        validation execution. line and marker must be stripped to remove trailing whitespace
        """
        value = MDParser.stripped(line).split(MDParser.stripped(validation_type))[1].strip()

        validation = {"type": validation_type, "value": value}

        return validation

    @staticmethod
    def parse_config_file_content(config_file_content):
        """
        Method parses config file and return specified variables dictionary
        :param config_file_content: - content of config file
        :return: dict variables with values
        """
        variables_dict = {}

        lines = config_file_content.split('\n')
        for line in lines:
            # process only lines not starting with # (skip comments)
            if len(line.strip()) > 0 and  line.strip()[0] != '#':
                k,v=line.split("=")

                if k.strip() == '':
                    raise(ValueError("variable name not present %s "% line))
                variables_dict[k.strip()] = v.strip()

        return  variables_dict

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

    parser.add_argument('--config-file',
                        default=None,
                        required=False,
                        help='Config file with variables to be injected')

    parser.add_argument('--all-executable',
                        default="no",
                        required=False,
                        choices=["yes", "no"],
                        help='If all lines except are executable')

    parser.add_argument('--intend',
                        default=0,
                        required=False,
                        help='Text indentation for script output (default 0)')

    parser.add_argument('--output-file',
                        default=None,
                        required=False,
                        help='File to store command, stderr, stdout , return code for all commands')

    parser.add_argument('--debug-env-vars',
                        default=None,
                        required=False,
                        help='Comma separated list of environment variables to be printed into output file for debugging')

    args = parser.parse_args()
    action = args.action
    input_file = args.input_file
    config_file_path = args.config_file
    all_executable = args.all_executable
    intend = args.intend
    output_file = args.output_file
    debug_env_vars = args.debug_env_vars

    if all_executable.lower() == "yes":
        all_executable = True
    elif all_executable.lower() == "no":
        all_executable = False
    else:
        print("Unknown value %a" % all_executable)

    # if output file is specified then check if path is writable
    # if path is not writhable raise exception
    if output_file is not None:
        try:
            f = open(output_file,"w")
            f.close()
        except:
            raise FileExistsError("Unable to create output file %s" %output_file)

    config_vars = {}
    if config_file_path is not None:
        if os.path.isfile(config_file_path) is True:
            config_file_content = MDParser.read_file(config_file_path)

            config_vars = MDParser.parse_config_file_content(config_file_content)
        else:
            print("File %s does not exist ! Exiting" % config_file_path)
            sys.exit(2)


    if action == "execute":
        mdp = MDParser(all_executable=all_executable, intend=intend, output_file=output_file, debug_env_vars=debug_env_vars)
        print("Processing file  %s" % input_file)
        mdp.execute_file(input_file, config_vars=config_vars)

    if action == "parse":

        mdp = MDParser()
        content = MDParser.read_file(input_file)
        parsed_output = MDParser.parse_md(content)
        mdp.print_parsed(parsed_output)
        analyzed_output = mdp.analyze_parsed(parsed_output)
        mdp.print_analyzed(analyzed_output)
