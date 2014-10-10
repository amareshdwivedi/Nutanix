from pip._vendor.html5lib.filters import optionaltags
__author__ = 'subashatreya'

from checkers.ncc_checker import NCCChecker
from checkers.vc_checker import VCChecker
from reporters import DefaultConsoleReporter
from PDFGenerator import PDFReportGenerator
from prettytable import PrettyTable
import json
import argparse
import sys
import os
import inspect
def exit_with_message(message):
    print message
    sys.exit(1)

def usage():
    x = PrettyTable(["Name", "Short help"])
    x.align["Name"] = "l"
    x.align["Short help"] = "l" # Left align city names
    x.padding_width = 1 # One space between column edges and contents (default)
    x.add_row(["ncc","Run checks against ncc module."])
    x.add_row(["vc","Run checks against vc module."])
    x.add_row(["run_all", "Run checks for all modules."])
    print x
    exit_with_message("")

def parse_args(args):
    if len(args)==0:
        usage()
    option=args[0]
    if option =='help':
        usage()
    if option not in ['ncc','vc','run_all']:
        usage()
    return option

def main():
    option = parse_args(sys.argv[1:])
    #checkers = {'ncc': NCCChecker(), 'vc': VCChecker()}
    '''
    fp = open("conf"+os.path.sep+"checkerObjects.conf", 'r')
    checkerObjectList = json.load(fp)
    fp.close()    
    checkers_to_run = []
    if option=="run_all":
        checkerslist = checkerObjectList.keys()
    else:
        checkerslist=[option]
         
    checkers = {}
    for checker in checkerslist:
#         if not checker in checkerObjectList.keys():
#             exit_with_message(checker + " is not valid checker")
        checkers[checker] = eval(checkerObjectList[checker])() 
    #print checkers
    '''
    #checkers = {'ncc': NCCChecker(), 'vc': VCChecker()}
    checkers_to_run = []   
    checkers = {}
    package = __import__("checkers")
    for modName, modObj in inspect.getmembers(package, inspect.ismodule):
        for className, classObj in inspect.getmembers(modObj, inspect.isclass):
            if not inspect.isabstract(classObj):
                try:
                    for xmodule in dir(package):
                        if xmodule.startswith('__'):
                            continue;
                        if xmodule == modName:
                            moduleFound = eval("package.%s"%modName)
                            for xclass in dir(moduleFound):
                                if xclass.startswith('__'):
                                    continue;
                                if xclass == className:
                                    xobj = eval("package.%s.%s"%(modName,className))
                                    if xobj._NAME_ in option or option=="run_all":
                                        checkers[xobj._NAME_] = xobj()
                                    break
                except:
                    # To skip the classes which are imported but not available in current module
                    #print "Exception -",sys.exc_info()[0]
                    continue
    #print "Avail checks :",checkers,option,type(option)
    if option=="run_all":
        checkerslist = checkers.keys()
    else:
        checkerslist=[option]
        
    for checker in checkerslist:
        fp = open("conf"+os.path.sep+checker+".conf", 'r')
        checker_config = json.load(fp)
        fp.close()
        checker_module = checkers[checker]
        reporter = DefaultConsoleReporter(checker)
        checker_module.configure(checker_config, reporter)
        if option=="run_all":
            checker_module.parse_args(['run_all'])
        else:
            checker_module.parse_args(sys.argv[2:])
#         if len(args.checks)!=0:
#             for item in args.checks :
#                 if item not in get_checks(checker):
#                     exit_with_message(str(args.checks) + " is not valid checks for "+ checker)
#             checker_module.checks=args.checks
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

