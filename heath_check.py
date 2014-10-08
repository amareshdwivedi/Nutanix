__author__ = 'subashatreya'

from checkers.ncc_checker import NCCChecker
from checkers.vc_checker import VCChecker
from reporters import DefaultConsoleReporter

import json
import argparse
import sys
import os

def exit_with_message(message):
    print message
    sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(description='Nutanix HealthCheck Tool')
    parser.add_argument('checkers', nargs='*', help="Checks you want to run")
    args = parser.parse_args()
    return args


def main():

    args = parse_args()
    
    #checkers = {'ncc': NCCChecker(), 'vc': VCChecker()}
    fp = open("conf"+os.path.sep+"checkerObjects.conf", 'r')
    checkerObjectList = json.load(fp)
    fp.close()    
    
    checkers_to_run = []
    if len(args.checkers) == 0:
        args.checkers = checkerObjectList.keys()
        
    checkers = {}
    for checker in args.checkers:
        if not checker in checkerObjectList.keys():
            exit_with_message(checker + " is not valid checker")
        checkers[checker] = eval(checkerObjectList[checker])() 
    #print checkers
    
    for checker in args.checkers:
        fp = open("conf"+os.path.sep+checker+".conf", 'r')
        checker_config = json.load(fp)
        fp.close()

        checker_module = checkers[checker]
        reporter = DefaultConsoleReporter(checker)
        checker_module.configure(checker_config, reporter)

        checkers_to_run.append(checker)

    results = {}

    for checker in checkers_to_run:

        checker_module = checkers[checker]
        result = checker_module.run_checks()
        results[checker] = result.to_dict()

    outfile = open("results.json", 'w')
    json.dump(results, outfile, indent=2)
    outfile.close()

if __name__ == "__main__":
    main()

