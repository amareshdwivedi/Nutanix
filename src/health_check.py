__author__ = 'subashatreya'

from checkers.ncc_checker import NCCChecker
from checkers.vc_checker import VCChecker
from checkers.view_checker import HorizonViewChecker
from checkers.base_checker import CheckerBase
from reporters import DefaultConsoleReporter
from report_generator import PDFReportGenerator,CSVReportGenerator
from prettytable import PrettyTable
import json
from operator import itemgetter
import csv, time
import sys
import os

def exit_with_message(message):
    print message+"\n"
    sys.exit(1)

def usage(checkers, message=None):

    x = PrettyTable(["Name", "Description"])
    x.align["Name"] = "l"
    x.align["Description"] = "l" # Left align city names
    x.padding_width = 1 # One space between column edges and contents (default)

    for checker in checkers:
        x.add_row([checker.get_name(), checker.get_desc()])

    x.add_row(["run_all", "Runs all health checks"])

    message = message is None and str(x) or "\nERROR : "+ message + "\n\n" + str(x)
    exit_with_message(message)


def main():
    checkers = {}
    for checker_class in CheckerBase.__subclasses__():
        checker = checker_class()
        checkers[checker.get_name()] = checker

    args = sys.argv[1:]
    if len(args) == 0:
        usage(checkers.values())

    option = args[0]

    if option == "run_all":
        checkers_list = checkers.keys()
        if len(args) > 1:
            usage(checkers.values(), "No parameter expected after run_all")
        else:
            # We need to pass through run_all arg to the module
            args.append("run_all")

    elif option == "help":
        usage(checkers.values(), None)

    elif option not in checkers.keys():
        usage(checkers.values(), "Invalid module name " + option)

    else:
        checkers_list=[option]


    # We call configure on each module first so that we can fail-fast
    # in case some module is not configured properly
    for checker in checkers_list:
        checker_conf_path=os.path.abspath(os.path.dirname(__file__))+os.path.sep +"conf" + os.path.sep + checker + ".conf"
        fp = open(checker_conf_path, 'r')
        checker_config = json.load(fp)
        fp.close()
        checker_module = checkers[checker]
        reporter = DefaultConsoleReporter(checker)
        checker_module.configure(checker_config, reporter)
 
    results = {}
 
    for checker in checkers_list:
 
        checker_module = checkers[checker]
        result = checker_module.execute(args[1:])
        results[checker] = result.to_dict()
        
        # This is to sort the checks in given checker based on the severity ( asc order )
        #try :
        #    results[checker]['checks'] = sorted(results[checker]['checks'], key=itemgetter('Severity'))
        #except KeyError:
            # It means no checks are executed for given checker
         #   continue
            
        
    healthcheckreportfolder=os.getcwd() + os.path.sep +"reports"
    if not os.path.exists(healthcheckreportfolder):
        os.mkdir(healthcheckreportfolder) 
 
        
    #Generate Json Reports 
    outfile = open(os.getcwd() + os.path.sep +"reports"+os.path.sep+"results.json", 'w')
    json.dump(results, outfile, indent=2)
    outfile.close()
    
    #Generate CSV Reports
    CSVReportGenerator(results)
        
    #Generate PDF Report based on results. 
    PDFReportGenerator(results)
     

if __name__ == "__main__":
    main()

