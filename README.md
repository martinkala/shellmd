# shellmd
Shell runner for documentation md files

### Description
Goal of the utility is to run code in codebloks within documentation md files.  
This approach allows dev-ops teams to store and maintain documentation in README.md files with runnable codeblocks.  If documentation is written according few simple rules, then it allows to automatically check if code in codeblocks is still up to date according current source code base.
Target area is automation on the sourcecode bases with support of utilities and processes documentation.   

In many cases documentation is spread in multiple places like company wiky, README.md files , static documents, tickets.
Shellmd is focused to environment where documentation is stored in MD files. In such case README.md is the last thing to be updated and often is not in sync with sourcecode or processes.
If md files are written in reasonable structure (see Shellmd docu style) then it is possible to use code block as executables in manual processing.
Together with any of integration platforms and shellmd can run automatic validation over your documentation.


Runnable codeblock are useful for utilities documentation and system procedures in README files. Also can be used to run automated checks to test if documentation and utilities and system are still in sync. 

### Supported executors
Curently only supported executor is linux bash. 

## Rules
 - documentation is written in code block encapsulated with standard md tags ```  
 - block to be executed should start with **#executable** on new line just after ```
 - all commands in code block have to be runnable in target OS
 - if no validation is executed on executed command, then expected commad have to finish successfully (return code is 0)

## Control comments
Control comments are simple one line directives to control codeblock execution. Those comments are written in user friendly form
so at the same moment commenst are controlling execution and describing to user expected beaviour.

### #executable
#executable is basic control comment at the beginning of code that we want to execute by shellmd. 
This block should be used only from the point we want to start execution.
```
#executable
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
#executable
ls bin/shellmd.py
#executable exact expected output is bin/shellmd.py
```


### #executable contains in expected output
Validation check if command output contains searched substring. Again only one line validations are possible 
```
#executable
ls -la
#executable contains in expected output ..
```
### #executable expected return code
Command return code is validated against desired value
```
#executable
mkdir error/error 
#executable expected return code 1
```

## How to run
Working examples based on linux system
```
#executable
python3 bin/shellmd.py --input-file=test/README_validations.md
python3 bin/shellmd.py --action=parse --input-file=test/README_validations.md
```

## Input parameters

 - --input-file - path to input md file 
 -  --action - action to be executed on md file
    - execute - default - will execute input md file
    - parse - only parses input md files, for correct parser output
 - --all-executable - yes/no - If yes ten all codeblocks in MD file will be executes. Even if #executable tag is not present int the block.

## Shellmd docu style
There are few tips how to write code blogs to be really useful.

- Each code block should be executable without additional setup
- Use setup for commands at the begining of the code block, or at least one code block should be defined as setup and other blo k then should refer to this setup
- Comment code block as real code 
- if possible each code block should work when copy pasted to console
- In scripts use paths defined in environment variables
- Define sll variables at the begining of the block
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
Such a code block is executable in console, easy to run in shellmd and also human readable.

### Shellmd limitations in code block
Shellmd executes each command independently on previous commands. So variable setup or directory change will not affect consequent commands.
- Do not use shell commands to 
  - change directory ( cd - will not work)
  - do not set environment variables for consequent commands, define variables in config file (export command will not work)
  - do not set environment properties, use shell wrappers if this is required ( set +e - wil not work)
- All required variables in codeblock insert into config file, or set to environment where you are running shellmd    

Example of previous block enriched by shellmd tags
```
# set required variables
SHELLMD_PATH=~/shellmd/
INPUT_MD_FILE=test/README_validations.md

#executable
# parse md file to discaver errors
python3 ${SHELLMD_PATH}/bin/shellmd.py --action=parse --input-file=${INPUT_MD_FILE}

# Execute md file in console
python3 ${SHELLMD_PATH}/bin/shellmd.py --input-file=${INPUT_MD_FILE}
#executable expected return code 0
```

## Internal documentation 
### How to run tests

Tests for bashmd are written in bats framework.
```
#executable
bats test/test_shellmd.bats
```

Unit test for parser and analyzer
```

#executable
python3 test/unit/parseTest.py
```
