Testing readme with codeblock execution


### Case simple shell command contains substring is std output
Expects std out contains ..
String .. is part of ls -la command
```
#executable
ls -la
#executable contains in expected output ..
```

### Case simple shell command and  exact std output match 
Expects std out contains filename shellmd.py as a result of ls bin/shellmd.py
```
#executable
ls bin/shellmd.py
#executable exact expected output is bin/shellmd.py
```

### Case simple shell command 
Return code expected 0 by default
```
#executable
ls -la
```


### Case simple shell command with return code expectation
Return code expected 0 by validation
```
#executable
ls -la
#executable expected return code 0
```

### Case simple shell command with non 0 return coded
Return code expected 1 by validation
```
#executable
mkdir error/error 
#executable expected return code 1
```