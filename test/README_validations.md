Testing readme with codeblock execution


### Case simple shell command contains substring is std output
Expects std out contains ..
String .. is part of ls -la command
```
#executable block
#executable contains in expected output ..
ls -la
```

### Case simple shell command and  exact std output match 
Expects std out contains filename shellmd.py as a result of ls bin/shellmd.py
```
#executable block
#executable exact expected output is bin/shellmd.py
ls bin/shellmd.py
```

### Case simple shell command 
Return code expected 0 by default
```
#executable block
ls -la
```


### Case simple shell command with return code expectation
Return code expected 0 by validation
```
#executable block
#executable expected return code 0
ls -la
```

### Case simple shell command with non 0 return code
Return code expected 1 by validation
```
#executable block
#executable expected return code 1
mkdir error/error 
```

### Case simple shell command with non 0 return code , space between command and comment char
Return code expected 1 by validation
```
# executable block
# executable expected return code 1
mkdir error/error 
```