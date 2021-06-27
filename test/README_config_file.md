Testing readme with codeblock execution --config-file
Variables are injecte before code blocks execution, 

### Case simple shell command with variables inject before code blocks execution
Expects variable TEST_VAR1 contains foo from injected config file
```
#executable block
#executable contains in expected output foo
echo ${TEST_VAR1}
```

Expects variable TEST_VAR2 contains bar from injected config file
```
#executable block
#executable contains in expected output bar
echo ${TEST_VAR2}
#executable contains in expected output /Home/User
echo ${UPPPER_VAR3}
```

### Case incorrect path to config file
Expects shell md fails on incorrect path to config file
```
#executable block
#executable expected return code 2
python3 bin/shellmd.py --config-file=/tmp/no_foo_bar --input-file=tests/README.md
```