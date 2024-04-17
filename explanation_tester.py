#!/usr/bin/env python
import tad
import util
from runner.explanation_driver import ExplanationDriver
from scripts.shared import parse_default_arguments


def main():
    args = parse_default_arguments()
    if args.endpoint is None:
        tad.check_for_servers(args)

    tad.api_test(args, ExplanationDriver(args))


if __name__ == "__main__":
    main()


def test_entry():
    main()
