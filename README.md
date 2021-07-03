# shellmd
Documentation validity checker

### Description
Goal of the utility periodically validate project documentation in md files. It is done by running code in codebloks within documentation md files.   
This approach allows dev-ops teams to store and maintain documentation in README.md files with runnable codeblocks.  If documentation is written according few simple rules, then it allows to automatically check if code in codeblocks is still up to date according current source code base.
Target area is automation on the sourcecode bases with support of utilities and processes documentation.   

In many cases documentation is spread in multiple places like company wiky, README.md files , static documents, tickets.
Shellmd is focused to environment where documentation is stored in MD files. In such case README.md is the last thing to be updated and often is not in sync with sourcecode or processes.
If md files are written in reasonable structure (see Shellmd docu style) then it is possible to use code block as executables in manual processing.
Together with any of integration platforms and shellmd can run automatic validation over your documentation.


Runnable codeblock are useful for documenting utilities and system procedures in README files and to run automated checks to test if documentation and utilities and system are still in sync.

### Supported executors
Curently only supported executor is bash on Linux and Mac. 

## Installation

Currenly only supported installation is possible from git hub

### Linux and Mac

```
export TARGET_DIR=~/
cd TARGET_DIR 
git clone https://github.com/martinkala/shellmd.git
```

### Under the hood
Shellmd uses python subprocess.Popen method to execute commands in code blocks. All environment variables from
current environment (the one that runs shellmd) are passed to environment where command is executed 

## Rules
Few simple rules alowing to shellmd parse your documentation in most effective way. 

 - documentation is written in code block encapsulated with standard md tags ```  
 - block to be executed should start with **#executable block start** on new line just after ```
 - all commands in code block have to be runnable in target OS
 - if no validation is executed on executed command, then expected commad have to finish successfully (return code is 0)

## Control comments
Control comments are simple one line directives to control codeblock execution. Those comments are written in user friendly form
so at the same moment commenst are controlling execution and describing to user expected beaviour.

### #executable block start
#executable is basic control comment at the beginning of code that we want to execute by shellmd. 
This block should be used only from the point we want to start execution.
```
#executable block start
ls -la
```

This behavior can be overridden by input parameter --all-executable=yes then all code blocks in MD file will be executed. 

## Validations
Validations are simple asserts .

With this can be checked 
 - exact match of standard output of command 
 - if standard output contains substring
 - return code of comand (also non zero)

### #executable exact expected output is
Exact match for command std out from command. Command std out is stripped therefore currently only one line output can be validated from command.
```
#executable exact expected output is bin/shellmd.py
ls bin/shellmd.py
```

### #executable contains in expected output
Validation check if command output contains searched substring. Again only one line validations are possible 
```
#executable contains in expected output ..
ls -la
```

### #executable expected return code
Command return code is validated against desired value
```
#executable expected return code 1
mkdir error/error 
```

## How to run
Working examples based on linux system
```
#executable block start
python3 bin/shellmd.py --input-file=test/README_validations.md
python3 bin/shellmd.py --action=parse --input-file=test/README_validations.md
```

## Input parameters

 - --input-file - path to input md file 
 -  --action - action to be executed on md file
    - execute - default value - will execute input md file
    - parse - only parses input md files, for correct parser output
 - --all-executable - yes/no - If yes then all codeblocks in MD file will be executed, even if #executable tag is not present int the block.
- --config-file - path to input config file with key=value variables for execution
- --output-file - File to store command, stderr, stdout , return code for all commands, check if path is writable before commands execution.
- --debug-env-vars -Comma separated list of environment variables to be printed into output file for debugging

Command will use config file with overriding variables, output file where detailed comamnds info is storred and vairables list to be printend in outpt file
```
python3 ${SHELLMD_PATH}/bin/shellmd.py --input-file=${SHELLMD_PATH}/test/README.md --output-file=${OUTPUT_FILE} --debug-env-vars=VVAARR1,VVAARR2
```

## Shellmd docu style
There are few tips how to write code blogs to be really useful.

- Each code block should be executable without additional setup
- Use setup for commands at the begining of the code block, or at least one code block should be defined as setup and other blocks should then refer to this setup
- Comment code block as real code 
- If possible each code block should work when copy/paste to console
- In scripts use paths defined in environment variables
- Define shell variables at the beginning of the block
- All parameters in commands write as variables

Example of shellmd docustyle
```
# set required variables
SHELLMD_PATH=~/shellmd/
INPUT_MD_FILE=test/README_validations.md

# parse md file to discaver errors
python3 ${SHELLMD_PATH}/bin/shellmd.py --action=parse --input-file=${INPUT_MD_FILE}

# Execute md file in console
python3 ${SHELLMD_PATH}/bin/shellmd.py --input-file=${INPUT_MD_FILE}
```
Such a code block is executable in console, easy to run in shellmd and also user friendly.

### Shellmd limitations in code block
Shellmd executes each command independently on previous commands, therefore variable setup or directory change will not affect consequent commands.
- Do not use shell commands to 
  - change directory ( cd - will not work)
  - do not set environment variables for consequent commands, define variables in config file (export command will not work)
  - do not set environment properties, use shell wrappers if this is required ( set +e - wil not work)
- All required variables in codeblock insert into config file, or set in environment where you are running shellmd    

Example of previous block enriched by shellmd tags
```
# set required variables
SHELLMD_PATH=~/shellmd/
INPUT_MD_FILE=test/README_validations.md

#executable block start
# parse md file to discaver errors
python3 ${SHELLMD_PATH}/bin/shellmd.py --action=parse --input-file=${INPUT_MD_FILE}

# Execute md file in console
#executable expected return code 0
python3 ${SHELLMD_PATH}/bin/shellmd.py --input-file=${INPUT_MD_FILE}
```

### config-file usage
Parameter --config-file (path to config file) allows user to specify set of variables to be set before execution.
This is useful when some of variables caanot be specified in documentation. In mostly cases those are secret, runtime 
or system based variables.
In such a case shellmd is capable to read simple text file with key=value pairs. Those variables will be inserted into
local shell md environment variables before execution.

Example od config file:
```
# variables to inject
TEST_VAR1=foo
TEST_VAR2=bar
```

- In config file are allowed comment lines starting with char # .
- In case multiple variables with the same name are specified , the last variable occurence is injecting into execution.
- If the same name of variable already exist in environemnt then config variable overrides original value 
(just for shellmd run) .
- Character = is not allowd in value part so if there is in one line character = more than once, then shell md 
throws error.
- If variable name is not specified only value with = character then shellmd throws error.
- If value is not specified only variable name then shellmd setes variable name to empty string.


## Internal documentation 
### How to run tests

Tests for shellmd are written in bats framework.
```
#executable block start
bats test/test_shellmd.bats
```

Unit test for parser and analyzer
```

#executable block start
python3 test/unit/parseTest.py
```

### Bats installation

```
#executable block start 
BATS_PATH=~/
mkdir -p ${BATS_PATH}

# clone all repositories
git clone https://github.com/bats-core/bats-core.git ${BATS_PATH}/bats-core
git clone https://github.com/ztombol/bats-assert.git ${BATS_PATH}/bats-assert
git clone https://github.com/ztombol/bats-support ${BATS_PATH}/bats-support

# make runnable for current user
mkdir -p ~/.local/bin
ln -s ${BATS_PATH}/bats-core/bin/bats ~/.local/bin/bats
```

## Shell md docker run

Shellmd can be started inside docker container. This approach requires to have prepared custom image with all dependenices resolved.
Simple example of run is
```
# executable block start
docker build -t shellmd -f Dockerfile .
docker run -it  shellmd /usr/bin/python3 /app/shellmd/bin/shellmd.py --input-file=/app/shellmd/test/README.md
```

To set shellmd in your custom contianer you can modify your docker file 
```
# debian based docker
RUN apt-get update && apt-get -y install python3 git 
RUN mkdir -p /app
git clone https://github.com/martinkala/shellmd /app/shellmd
COPY . /app/shellmd
```