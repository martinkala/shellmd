# shellmd
Shell runner for documentation md files

### Description
Goal of utilty is to to runs code encapsulated in codebloks in md files. This approach allows dev-ops teams to store and maintain documentation with runable codeblocks.  If documetation is written according few simple rules it allows to automatically check if code in codeblocks are still up to date according current source code base.

### Supported executors
Currently only supported executor is linux bash. 

## Rules
 - documentation is written in code block encapsulated with standard md markers ```  
 - block to be executed starts with #executable on new line just after ```
 - all commands in code block are runable in target OS
 - if no validation is executed on executed command, then expected return code is 0

## Validations
In case script want to expect output of documentation command is possible to check standard output of command or
if standard output contains substring.

 - #executable expected output
 - #executable expected output contains

## How to run
Working examples based on linux system
```
python3 bin/shellmd.py --input-file=test/README_validations.md
python3 bin/shellmd.py --action=parse --input-file=test/README_validations.md
```
