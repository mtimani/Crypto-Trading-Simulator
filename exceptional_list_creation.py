#!/usr/bin/python3


#----------------Imports----------------#
import json
import sys
import argparse
import os
import os.path
from pygments import highlight
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.lexers.web import JsonLexer
from termcolor import colored, cprint



#-----------Global variables------------#
max_nb_strategies = 3



#-----Validate Directory Parameter------#
class validateDirectoryParameter(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        global max_nb_strategies

        if not os.path.isdir(values):
            parser.error(f"Please enter a valid directory that contains results from previous tests. Got: {values}")
        else:
            exists = False
            for strategy in range(1, max_nb_strategies + 1):
                if os.path.isfile(values + "/Strategy_" + str(strategy) + "_testing/exceptional.json"):
                    exists = True
            if not exists:
                parser.error(f"Please enter a valid directory that contains results from previous tests. Got: {values}")
        setattr(namespace, self.dest, values)



#-----Validate Strategy Parameters------#
class validateStrategiesParameters(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        global max_nb_strategies

        allowed_values = []
        for i in range(1,max_nb_strategies+1):
            allowed_values.append(str(i))

        for i in values:
            if not (i in allowed_values):
                parser.error(f"Please enter valid strategies to test. Allowed strategies are between 1 and " + str(max_nb_strategies) + ". Got: " + str(values))
                break

        setattr(namespace, self.dest, values)



#--------Arguments Parse Function-------#
def parse_command_line():
    ## Global variables
    global max_nb_strategies

    ## Arguments groups
    parser      = argparse.ArgumentParser()
    required    = parser.add_argument_group('required arguments')
    exclusive   = parser.add_argument_group('mutually exclusive arguments')
    content     = exclusive.add_mutually_exclusive_group(required=True)

    ## Arguments
    parser.add_argument("-l", "--logging", action='store_true', dest="logging", help="enable logging in the console")
    required.add_argument("-d", "--directory", dest="directory", help="directory that contains results from previous tests", required=True, action=validateDirectoryParameter)
    content.add_argument("-a", "--all", action='store_true', dest="all", help="run script with all strategies")
    content.add_argument("-s", "--strategies", dest="strategy", nargs='+', help="run script with specific strategies (allowed strategies between 1 and " + str(max_nb_strategies) + ")",  action=validateStrategiesParameters)
    return parser



#-------------Main Function-------------#
def main(args):
    ## Variables
    global max_nb_strategies
    directory               = args.directory
    logging                 = args.logging
    run_all_strategies      = args.all
    run_specific_strategies = args.strategy 
    final                   = {}
    strategies              = []

    ## Strategies list population
    ### If option -a is specified
    if run_all_strategies:
        for i in range(1, max_nb_strategies + 1):
            strategies.append(str(i))
    ### If option -s is specified
    elif len(run_specific_strategies) != 0:
        strategies = sorted(set(run_specific_strategies)).copy()

    ## Output to console if logging is enabled
    if logging:
        log_text = "\n[INFO]\t\tLaunching exceptional_list_creation.py script for the following strategies: " + strategies[0]
        if len(strategies) > 1:
            for strat in strategies[1:-1]:
                log_text += ", " + strat
            log_text += " and " + strategies[-1]
        cprint(log_text, 'blue')

    ## Create output directories
    try:
        os.mkdir(directory + "/Exceptional_combination")
        if logging:
            cprint("[INFO]\t\tCreation of " + directory + "/Exceptional_combination directory", 'blue')
    except FileExistsError:
        if logging:
            cprint("[INFO]\t\tDirectory " + directory + "/Exceptional_combination already exists", 'blue')
        else:
            None
    except:
        raise

    ## Open exceptional files
    for strategy in strategies:
        with open(directory + "/Strategy_" + strategy + "_testing/exceptional.json", "r") as fp:
            tmp = json.load(fp)

        for coin in tmp:
            if coin in final:
                if final[coin]["average"] < tmp[coin]["average"]:
                    final[coin] = tmp[coin].copy()
            else:
                final[coin] = tmp[coin].copy()
    
    ## Format JSON
    formatted_final = json.dumps(final, sort_keys=True, indent=4)

    ## Display to console if the logging is on
    if logging:
        colorful = highlight(formatted_final, lexer=JsonLexer(), formatter=Terminal256Formatter())
        print(colorful)
    
    ## Write exceptional to file
    output_file = directory + "/Exceptional_combination/exceptional_final.json"
    with open(output_file, "w") as fp:
        fp.write(json.dumps(final, sort_keys=True, indent=4))



#-----------Main Function Call----------#
if __name__ == "__main__":
    args = parse_command_line().parse_args()
    main(args)
