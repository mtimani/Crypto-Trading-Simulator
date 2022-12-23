#!/usr/bin/python3


#----------------Imports----------------#
import sys
import argparse
import json
import os
import os.path
import subprocess
import datetime
from pygments import highlight
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.lexers.web import JsonLexer
from termcolor import colored, cprint



#-----------Global variables------------#
max_nb_strategies = 6
max_allowed_year = int(datetime.date.today().strftime("%Y"))
min_allowed_year = 2017



#-----Validate Directory Parameter------#
class validateDirectoryParameter(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        global max_nb_strategies

        if not os.path.isdir(values):
            parser.error(f"Please enter a valid directory. Got: {values}")
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
    content.add_argument("-a", "--all", action='store_true', dest="all", help="run all scripts for all strategies")
    content.add_argument("-s", "--strategies", dest="strategy", nargs='+', help="run specific strategies (allowed strategies between 1 and " + str(max_nb_strategies) + ")",  action=validateStrategiesParameters)
    return parser



#-------------Main Function-------------#
def main(args):
    ## Variables
    global max_nb_strategies
    global max_allowed_year
    directory               = args.directory
    logging                 = args.logging
    run_all_strategies      = args.all
    run_specific_strategies = args.strategy 
    strategies              = []
    final                   = {}

    ## Strategies list population
    ### If option -a is specified
    if run_all_strategies:
        for i in range(1, max_nb_strategies + 1):
            strategies.append(str(i))
    ### If option -s is specified
    elif len(run_specific_strategies) != 0:
        strategies = sorted(set(run_specific_strategies)).copy()

    ## Output to console
    log_text = "\n[INFO]\t\tLaunching all scripts for the following strategies: " + strategies[0]
    if len(strategies) > 1:
        for strat in strategies[1:-1]:
            log_text += ", " + strat
        log_text += " and " + strategies[-1]
    cprint(log_text, 'blue')

    ## Launching strategy_testing.py script
    for strat in strategies:
        try:
            bashCommand = "python3 strategy_testing.py -d " + directory + " -s " + strat
            if logging:
                bashCommand += " -l"
            os.system(bashCommand)
        except:
            cprint("[ERROR]\t\tAn error occured while trying to run strategy_validation.py script with the strategy number " + strat, 'red')
            strategies.remove(strat)

    ## Creating strategies string
    strategies_str = ""
    for strat in strategies:
        strategies_str += strat + " "
    
    ## Check if strategy_testing.py script did not totally fail
    if len(strategies) > 0:
        ### Boolean to check if strategy_validation.py script can be ran
        validation_can_run = True

        ### Launching exceptional_list_creation.py script
        try:
            bashCommand = "python3 exceptional_list_creation.py -d " + directory + " -s " + strategies_str
            if logging:
                bashCommand += " -l"
            os.system(bashCommand)
        except:
            cprint("\n[ERROR]\t\tAn error occured while trying to run exceptional_list_creation.py script with the following strategy numbers " + str(strategies), 'red')

        ### Launching statistics.py script
        try:
            bashCommand = "python3 statistics.py -d " + directory + " -s " + strategies_str
            if logging:
                bashCommand += " -l"
            os.system(bashCommand)
        except:
            cprint("\n[ERROR]\t\tAn error occured while trying to run statistics.py script with the following strategy numbers " + str(strategies), 'red')
            validation_can_run = False

        ### Check if strategy_validation.py script can be ran
        if not(validation_can_run):
            cprint("\n[ERROR]\t\tThe script strategy_validation.py cannot be ran, because the statistics.py script failed to run", 'red')   
        else:
            #### Check if Statistics/exceptional_final.json file exists
            if not (os.path.isfile(directory + "/Statistics/statistics.json")):
                cprint("\n[ERROR]\t\tThe script strategy_validation.py cannot be ran, because the statistics file is absent", 'red')
            else:
                #### Load Statistics/exceptional_final.json file contents
                with open(directory + "/Statistics/statistics.json", "r") as fp:
                    statistics = json.load(fp)

                #### Create a dictionary to store parameters for the strategy_validation.py script
                to_validate = {}

                #### Populate to_validate dictionary
                for strat in strategies:
                    key = "strategy_" + strat
                    if not(key in statistics):
                        strategies.remove(strat)
                    else:
                        sl  = list(statistics[key]["Exceptional"]["Most frequent losses"])[0]
                        ema = list(statistics[key]["Exceptional"]["Most frequent EMA for most frequent loss"])[0]
                        to_validate[strat] = {"sl": sl, "ema": ema}

                #### Run the strategy_validation.py script
                for strat in strategies:
                    for year in range(max_allowed_year - 2,max_allowed_year + 1):
                        try:
                            losses = int(100 - float(to_validate[strat]["sl"])*100)
                            ema    = int(float(to_validate[strat]["ema"]))
                            bashCommand = "python3 strategy_validation.py -d " + directory + " -s " + strat + " -m " + str(losses) + " -e " + str(ema) + " -y " + str(year)
                            if logging:
                                bashCommand += " -l"
                            os.system(bashCommand)
                        except:
                            cprint("[ERROR]\t\tAn error occured while trying to run strategy_validation.py script with the strategy number " + strat, 'red')
                            strategies.remove(strat)
    
    ## Launch history_strategy.py script
    try:
        ### Check if 
        if not(os.path.isfile(directory + "/Exceptional_combination/exceptional_final.json")):
            cprint("[ERROR]\t\tAn error occured while trying to run history_strategy.py script, " + directory + "/Exceptional_combination/exceptional_final.json file is absent", 'red')
        else:
            for year in range(max_allowed_year - 3, max_allowed_year + 1):
                bashCommand = "python3 history_strategy.py -d " + directory + " -y " + str(year)
                if logging:
                    bashCommand += " -l"
                os.system(bashCommand)
    except:
        cprint("[ERROR]\t\tAn error occured while trying to run history_strategy.py script", 'red')

    ## Output to console
    cprint("\n\n[INFO]\t\tAll tests complete",'blue')



#-----------Main Function Call----------#
if __name__ == "__main__":
    args = parse_command_line().parse_args()
    main(args)
