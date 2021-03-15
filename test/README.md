Testing readme with codeblock execution

### Case simple shell command 
Return code expected 0
```
#executable
ls -la
```

### Case multiple shell commands in one block
Return code expected 0
```
#executable
ls -la
pwd
env
sleep 1
```

### Case run script using bash
Return code expected 0
```
#executable
bash test/tst.sh
```


