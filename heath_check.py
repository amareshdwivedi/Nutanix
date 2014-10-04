__author__ = 'subashatreya'

from checkers.ncc_checker import NCCChecker
from checkers.vc_checker import VCChecker
from reporters import DefaultConsoleReporter

import json
import argparse
import sys

def exit_with_message(message):
    print message
    sys.exit(1)

def parse_args():
    parser = argparse.ArgumentParser(description='Nutanix HealthCheck Tool')
    parser.add_argument("configfile", help="Input json file with configuration")
    parser.add_argument('checkers', nargs='*', help="Checks you want to run", default='all')
    args = parser.parse_args()
    return args

def main():

    args = parse_args()
    fp = open(args.configfile, 'r')
    config = json.load(fp)
    fp.close()

    checkers = {'ncc': NCCChecker(), 'vc': VCChecker()}
    reporters = {}

    checkers_to_run = []
    for checker in args.checkers:
        if not checker in checkers:
            exit_with_message(checker + " is not valid checker")
        if not checker in config:
            exit_with_message(checker + " does not have configuration")

        checker_config = config[checker]
        checker_module = checkers[checker]
        checker_module.configure(checker_config)

        checkers_to_run.append(checker)

    results = {}

    for checker in checkers_to_run:
        reporter = DefaultConsoleReporter(checker)
        reporters[checker] = reporter
        checker_module = checkers[checker]
        result = checker_module.run_checks(reporter)
        results[checker] = result.to_dict()

    outfile = open("results.json", 'w')
    json.dump(results, outfile, indent=2)
    outfile.close()

if __name__ == "__main__":
    main()

