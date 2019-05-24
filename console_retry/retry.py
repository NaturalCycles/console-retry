#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""retry.py: Requires python 3.5+. Run a shell command with maximum timeout on stdout output. Retry if it there is
   no output in specified timeout."""

__author__ = "Kristofer Borgström"


import sys
import time
import asyncio
from subprocess import PIPE

import argparse


async def run_command(command, timeout=None):
    """
    Async function to execute command. Returns tuple of return code and boolean specifying whether timeout was reached.

    TODO: Make it beatiful AND work.
    TODO: automate testing, some tests run manually:

    """
    process = await asyncio.create_subprocess_shell(command, stdout=PIPE, stderr=PIPE)
    timed_out = False
    start = time.time()

    full_output = ""
    inner_timeout = 1
    # read line (sequence of bytes ending with b'\n') asynchronously
    received_output = True  # Not really true but we want to initilize timeout
    exit_now = False
    while True:
        if received_output:
            # We got some data, update timeout
            if timeout:
                time_out_at = time.time() + timeout
            else:
                time_out_at = time.time() + 60 * 60 * 24 * 365  # ~1 year ~= infinite
            received_output = False
        try:
            line = await asyncio.wait_for(process.stdout.readline(), inner_timeout)
        except asyncio.TimeoutError:
            # reached inner timeout, do nothing
            pass
        else:
            if not line:  # EOF
                exit_now = True
            else:
                line = line.decode('utf-8').rstrip()
                full_output += line + "\n"
                print(line)
                sys.stdout.flush()  # Force flush
                received_output = True
                continue

        try:
            line = await asyncio.wait_for(process.stderr.readline(), inner_timeout)
        except asyncio.TimeoutError:
            # reached inner timeout, do nothing
            pass
        else:
            if not line:  # EOF
                exit_now = True
            else:
                line = line.decode('utf-8').rstrip()
                full_output += line + "\n"
                print(line)
                sys.stdout.flush()  # Force flush
                received_output = True
                continue

        if exit_now:
            break

        if time.time() > time_out_at:
            print("RETRY: Reached timeout after %d seconds, killing process" % timeout)
            timed_out = True
            process.kill()
            break

    returncode = await process.wait()
    elapsed = time.time() - start

    return returncode, timed_out, elapsed, full_output  # wait for the child process to exit


def main():

    argparser = argparse.ArgumentParser(description='Run a shell command with maximum timeout on stdout output. '
                                                    'Retry if it there is no output in specified timeout.')
    argparser.add_argument('command', metavar='command', nargs=1,
                           help='the ("quoted") command to monitor output for and retry')
    argparser.add_argument('-p', dest='progressive', action='store_const', const=True,
                           default=False,
                           help='Increase timeout progressively (x2 per retry).')
    argparser.add_argument('-r', dest='retries', type=int,
                           default=3,
                           help='Maximum amount of retries. Default is 3')
    argparser.add_argument('-s', dest='skiplast', action='store_const', const=True,
                           default=False,
                           help='Skip timeout on last retry attempt (infinite timeout)')
    argparser.add_argument('-o', dest='retry_outputs', action='append',
                           help='if command output contains this string, retry will run despite returning error code')
    argparser.add_argument('-t', dest='timeout', type=int,
                           default=60,
                           help='Timeout for standard out. Default is 60')

    args = argparser.parse_args()

    loop = asyncio.get_event_loop()
    line_timeout = args.timeout

    # Join argparse array into string and remove line breaks - "it's a feature, not a bug". It's there because circleci
    # adds line breaks between test files
    command = " ".join(args.command).replace('\n', ' ').replace('\r', '')

    for i in range(args.retries):
        if args.skiplast and i + 1 == args.retries:
            line_timeout = None  # Disable timeout on last attempt if run with -s

        print("RETRY: Executing command: %s, with timeout: %s" % (command, line_timeout))  # %s to allow None
        (returncode, timedOut, elapsed, output) = loop.run_until_complete(run_command(command, timeout=line_timeout))

        if not timedOut:
            print("RETRY: Command finished in (%d) seconds with exit code: %d" % (elapsed, returncode))

            retry = False
            if args.retry_outputs and returncode != 0:

                for retry_output in args.retry_outputs:
                    if retry_output in output:
                        print("RETRY: Found string: \"%s\" in command output, retrying despite error code" %
                              retry_output)
                        retry = True
                        break

            if not retry:
                sys.exit(returncode)

        print("RETRY: Command timed out")

        if i < args.retries - 1:  # We will try again
            if args.progressive:
                print("RETRY: Increasing timeout and trying again")
                line_timeout = line_timeout * 2
            else:
                print("RETRY: Trying again...")

    print("RETRY: Command never finished successfully")

    sys.exit(1)
