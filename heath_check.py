__author__ = 'subashatreya'

from checkers.ncc_checker import NCCChecker
from checkers.vc_checker import VCChecker
from reporters import DefaultConsoleReporter
from PDFGenerator import PDFReportGenerator

import json
import argparse
import sys
import os

def exit_with_message(message):
    print message
    sys.exit(1)


def parse_args():
    class MyAction(argparse.Action):
        def __call__(self,parser,namespace,values,option_string=None):
            if not values:
                setattr(namespace,self.dest,[0])
            else:
                setattr(namespace,self.dest,values)
    
    parser = argparse.ArgumentParser(description='Nutanix HealthCheck Tool')
    #parser.add_argument('checkers', nargs='*', help="Checkers you want to run")
    checkers=get_checkers()
    checks=[]
    for checker in checkers:
        checks.extend(get_checks(checker))
    parser.add_argument('-checkers',default=[],choices=checkers,action=MyAction,nargs="+")
    parser.add_argument('-checks',default=[],choices=checks,action=MyAction,nargs="+")
    args = parser.parse_args()
    return args

def get_checkers():
    fp = open("conf"+os.path.sep+"checkerObjects.conf", 'r')
    checkerObjectList = json.load(fp)
    fp.close()
    return checkerObjectList.keys()

def get_checks(checker):
    fp = open("conf"+os.path.sep+checker+".conf", 'r')
    checker_config = json.load(fp)
    fp.close()
    checks_list = [k for k,v in checker_config.items() if k.endswith('checks')]   
    return checks_list
    

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
        if len(args.checks)!=0:
            for item in args.checks :
                if item not in get_checks(checker):
                    exit_with_message(str(args.checks) + " is not valid checks for "+ checker)
            checker_module.checks=args.checks
        checkers_to_run.append(checker)

    results = {}

    for checker in checkers_to_run:

        checker_module = checkers[checker]
        result = checker_module.run_checks()
        results[checker] = result.to_dict()
    #Generate PDF Report based on results
    PDFReportGenerator(results);
    outfile = open("results.json", 'w')
    json.dump(results, outfile, indent=2)
    outfile.close()

if __name__ == "__main__":
    main()

