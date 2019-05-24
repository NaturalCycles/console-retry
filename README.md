# console-retry

This utility is designed to run any shell command and retry if no new line was written to 
stdout within a specified timeout. Especially useful in CI to retry flaky tests/scripts

The default timeout applies to lines written to stdout of the shell command. 

Retry is triggered when:
* No new line was written to stdout after specified timeout

Retry is not triggered when:
* The command as a whole takes longer than specified timeout
* The command returns a non-zero (error) return code

To be a good bash-citizen the return code is mirrors the return code of the subcommand or 1 if the command never 
finished in the specified timeout.

# Example use / tests

```
console-retry -t 10 "echo abcd ; false" # Immediate fail
console-retry -r 1 "sleep 70" # Fail after default timeout = 60
console-retry -s -r 1 -t 10 "sleep 15" # Should "skip timeout and therefore succeed after 15s"
console-retry -t 10 "echo abcd ; true" # Immediate success
console-retry -p -o abcd -t 10 " sleep 5; echo abc ;sleep 20; false" # Should Complete with error on second try
console-retry -o abcd -t 10 " sleep 5; echo abc ;sleep 20; false" # Should fail after retrymax (no progressive)
console-retry -o abc -t 10 " sleep 5; echo abc ; false"           # Should retry max but never with ok
console-retry -o abc -t 10 ">&2 echo abc ; false"                 # stderr, should retry max
console-retry -o nomatch -t 10 ">&2 echo abc ; false"             # stderr, should fail immediately
console-retry -o abc -t 10 "echo abc ; true"                      # stderr, should succeed immediately
console-retry -o nomatch -t 10 ">&2 echo abc ; sleep 2; echo def; true"  # Output should be: abc \ndef
console-retry -t 10 ">&2 echo abc ; sleep 10; echo def; sleep 10; true" # Staggered output 
```