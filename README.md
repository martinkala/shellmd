# shellmd
Shell runner for documentation md files

### Description
Goal of utility is to to run code encapsulated in codebloks in input md files. 
This approach allows dev-ops teams to store and maintain documentation in README.md files with runnable codeblocks.  If documentation is written according few simple rules, then it allows to automatically check if code in codeblocks is still up to date according current source code base.

Runnable codeblock are useful for documenting utilities and system procedures in README files and to run automated checks to test if documentation and utilities and system are still in sync. 
### Supported executors
Currently only supported executor is linux bash. 

## Rules
 - documentation is written in code block encapsulated with standard md markers ```  
 - block to be executed starts with #executable on new line just after ```
 - all commands in code block are runable in target OS
 - if no validation is executed on executed command, then expected return code is 0

## Controll commens
Validations are simple one line comments to control codeblock execution. Those comments are writen in human readable form
so at the same moment can control execution and describe command expected beavior.

### #executable
Basic control comment at the beginning of code block marks block for execuion. 
In case not block are intended for execution this mark can set only those we want ot execute.
```
#executable
ls -la
```

This behavior can be overridden by input parameter --all-executable=yes then all code blocks in MD file will be executed. 

## Validations
In case script want to expect output of documentation command is possible to check standard output of command or
if standard output contains substring.

### #executable exact expected output is
Exact match for command std out from command. Command std out is stripped so currently only one line output can be validated from command.
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
python3 bin/shellmd.py --input-file=test/README_validations.md
python3 bin/shellmd.py --action=parse --input-file=test/README_validations.md
```

## Input parameters

 - --input-file - path to input md file 
 -  --action - action to be executed on md file
    - execute - default - will execute input md file
    - parse - only parses input md files, for correct parser output