import os
import sys
import logging
from argparse import ArgumentParser, RawTextHelpFormatter

from .settings import (
    CLI_HELP_TEXT,
    CONFIG_FILE,
    PROGRAM_NAME_VERBOSE,
    PROGRAM_VERSION,
    STREAM_LOGGERS
)


# -----------------------------------------------------------------------------
# CLI Definition

def cli(argv):
    """
    Initialize our argument parser given arguments and
    return the parsed args & parser.
    """

    # argv[0] is always the filename being executed.
    # In this case it is the name of our program/entry point.
    program_name = argv[0]

    # Create an argument parser to handle our command line arguments.
    parser = ArgumentParser(
        prog=program_name,
        description=CLI_HELP_TEXT,
        formatter_class=RawTextHelpFormatter
    )

    # Verbose mode switch
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='enable verbose console'
    )

    # Output program version information.
    parser.add_argument(
        '--version',
        action='version',
        version=f'{PROGRAM_NAME_VERBOSE} {PROGRAM_VERSION}'
    )

    # Parse the arguments via our argument parser.
    args = parser.parse_args(argv[1:])

    if args.verbose is not None and args.verbose:
        STREAM_LOGGERS.append((logging.DEBUG, sys.stdout))

    # Return our args and the parser for parser.print_help(), etc.
    return (args, parser)
