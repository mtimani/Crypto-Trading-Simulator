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
max_nb_strategies = 7



#-----Validate Directory Parameter------#
class validateDirectoryParameter(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        global max_nb_strategies

        if not os.path.isdir(values):
            parser.error(f"Please enter a valid directory that contains results from previous tests. Got: {values}")
        else:
            exists = False
            for strategy in range(1, max_nb_strategies + 1):
                if os.path.isfile(values + "/Strategy_testing/Strategy_" + str(strategy) + "_testing/exceptional.json"):
                    if os.path.isfile(values + "/Strategy_testing/Strategy_" + str(strategy) + "_testing/optimized_out.json"):
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

    ## Output to console
    log_text = "\n[INFO]\t\tLaunching statistics.py script for the following strategies: " + strategies[0]
    if len(strategies) > 1:
        for strat in strategies[1:-1]:
            log_text += ", " + strat
        log_text += " and " + strategies[-1]
    cprint(log_text, 'blue')

    ## Check if all directories are populated (so that the sript can properly run)
    for strategy in strategies:
        if not (os.path.isfile(directory + "/Strategy_testing/Strategy_" + str(strategy) + "_testing/exceptional.json")):
            cprint("[ERROR]\t\tPlease enter a valid directory that contains results from previous tests. Got: " + directory, 'red')
            raise SystemExit(1)
        if not (os.path.isfile(directory + "/Strategy_testing/Strategy_" + str(strategy) + "_testing/optimized_out.json")):
            cprint("[ERROR]\t\tPlease enter a valid directory that contains results from previous tests. Got: " + directory, 'red')
            raise SystemExit(1)

    ## Create output directories
    try:
        os.mkdir(directory + "/Statistics")
        if logging:
            cprint("[INFO]\t\tCreation of " + directory + "/Statistics directory", 'blue')
    except FileExistsError:
        if logging:
            cprint("[INFO]\t\tDirectory " + directory + "/Statistics already exists", 'blue')
        else:
            None
    except:
        raise

    ## Check if an statistics file already exists
    output_file = directory + "/Statistics/statistics.json"
    if os.path.isfile(output_file):
        with open(output_file, "r") as fp:
            final = json.load(fp)

    ## Loop through strategies
    for strategy in strategies:
        ### Output to console if logging is enabled
        if logging:
            cprint("\n[INFO]\t\tStarting strategy " + str(strategy) + " statistical analysis", 'blue')

        ### Open exceptional files
        with open(directory + "/Strategy_testing/Strategy_" + str(strategy) + "_testing/exceptional.json", "r") as fp:
            #### Load content from exceptional.json file
            exceptional = json.load(fp)

            #### Output to console if logging is enabled
            if logging:
                cprint("[INFO]\t\tOpening " + directory + "/Strategy_testing/Strategy_" + str(strategy) + "_testing/exceptional.json file", 'blue')
        
        ### Open optimized_out files
        with open(directory + "/Strategy_testing/Strategy_" + str(strategy) + "_testing/optimized_out.json", "r") as fp:
            #### Load content from optimized_out.json file
            optimized_out = json.load(fp)

            #### Output to console if logging is enabled
            if logging:
                cprint("[INFO]\t\tOpening " + directory + "/Strategy_testing/Strategy_" + str(strategy) + "_testing/optimized_out.json file", 'blue')

        ### Variable initialization exceptional
        number_of_exceptional_entries_by_losses = {}
        number_of_exceptional_entries_by_ema_window = {}

        #### Output to console if logging is enabled
        if logging:
            cprint("[INFO]\t\tStarting analysis of " + directory + "/Strategy_testing/Strategy_" + str(strategy) + "_testing/exceptional.json file", 'blue')

        ### Loop through exceptional entries
        for coin in exceptional:
            #### Loss entries numbers calculation
            current_loss = exceptional[coin]["sl"]
            if not (current_loss in number_of_exceptional_entries_by_losses):
                number_of_exceptional_entries_by_losses[current_loss]  = 1
            else:
                number_of_exceptional_entries_by_losses[current_loss] += 1

            #### EMA entries numbers calculation
            current_ema  = exceptional[coin]["ema_window"]
            if not (current_ema in number_of_exceptional_entries_by_ema_window):
                number_of_exceptional_entries_by_ema_window[current_ema]  = 1
            else:
                number_of_exceptional_entries_by_ema_window[current_ema] += 1
        
        ### Maximums from exceptional entries
        max_loss_exceptional    = max(number_of_exceptional_entries_by_losses, key=number_of_exceptional_entries_by_losses.get)
        max_loss_exceptional_nb = max(number_of_exceptional_entries_by_losses.values())
        max_ema_exceptional     = max(number_of_exceptional_entries_by_ema_window, key=number_of_exceptional_entries_by_ema_window.get)
        max_ema_exceptional_nb  = max(number_of_exceptional_entries_by_ema_window.values())

        ### Variable initialization exceptional bis
        number_of_exceptional_entries_by_ema_window_with_losses = {}

        ### Loop through exceptional entries bis
        for coin in exceptional:
            #### Loss entries numbers calculation
            current_loss = exceptional[coin]["sl"]
            if current_loss == max_loss_exceptional:
                current_ema = exceptional[coin]["ema_window"]
                if not (current_ema in number_of_exceptional_entries_by_ema_window_with_losses):    
                    number_of_exceptional_entries_by_ema_window_with_losses[current_ema]  = 1
                else:
                    number_of_exceptional_entries_by_ema_window_with_losses[current_ema] += 1

        max_ema_for_max_loss    = max(number_of_exceptional_entries_by_ema_window_with_losses, key=number_of_exceptional_entries_by_ema_window_with_losses.get)
        max_ema_for_max_loss_nb = max(number_of_exceptional_entries_by_ema_window_with_losses.values())

        ### Variable initialization optimized
        number_of_optimized_entries_by_losses = {}
        number_of_optimized_entries_by_ema_window = {}
        max_ema_optimized_for_exceptional_ema_for_max_loss = 0

        #### Output to console
        cprint("[INFO]\t\tStarting analysis of " + directory + "/Strategy_testing/Strategy_" + str(strategy) + "_testing/optimized_out.json file", 'blue')

        ### Loop through optimized_out entries
        for coin in optimized_out["results"]:         
            #### Loss entries numbers calculation
            current_loss = optimized_out["results"][coin]["sl"]
            if not (current_loss in number_of_optimized_entries_by_losses):
                number_of_optimized_entries_by_losses[current_loss]  = 1
            else:
                number_of_optimized_entries_by_losses[current_loss] += 1

            #### EMA entries numbers calculation
            current_ema  = optimized_out["results"][coin]["ema_window"]
            if not (current_ema in number_of_optimized_entries_by_ema_window):
                number_of_optimized_entries_by_ema_window[current_ema]  = 1
            else:
                number_of_optimized_entries_by_ema_window[current_ema] += 1

            #### EMA entries numbers calculation bis
            current_ema  = optimized_out["results"][coin]["ema_window"]
            if current_ema == max_ema_for_max_loss:
                max_ema_optimized_for_exceptional_ema_for_max_loss += 1

        ### Maximums from exceptional entries
        max_loss_optimized    = max(number_of_optimized_entries_by_losses, key=number_of_optimized_entries_by_losses.get)
        max_loss_optimized_nb = max(number_of_optimized_entries_by_losses.values())
        max_ema_optimized     = max(number_of_optimized_entries_by_ema_window, key=number_of_optimized_entries_by_ema_window.get)
        max_ema_optimized_nb  = max(number_of_optimized_entries_by_ema_window.values())

        ### Return extraction
        optimized_return_average = optimized_out["average"]

        ### Add results to final dictionnary
        final["strategy_" + str(strategy)] = {"Average": optimized_return_average, "Exceptional": {"Most frequent losses": {str(max_loss_exceptional): max_loss_exceptional_nb}, "Most frequent EMA": {str(max_ema_exceptional): max_ema_exceptional_nb}, "Most frequent EMA for most frequent loss": {str(max_ema_for_max_loss): max_ema_for_max_loss_nb}}, "Optimized": {str(max_loss_optimized): max_loss_optimized_nb, str(max_ema_optimized): max_ema_optimized_nb, str(max_ema_for_max_loss).split('.')[0]+"_exceptional": max_ema_optimized_for_exceptional_ema_for_max_loss}}

    ## Format JSON
    formatted_final = json.dumps(final, sort_keys=True, indent=4)

    ## Display to console if the logging is on
    if logging:
        colorful = highlight(formatted_final, lexer=JsonLexer(), formatter=Terminal256Formatter())
        print(colorful)
    
    ## Write exceptional to file
    output_file = directory + "/Statistics/statistics.json"
    with open(output_file, "w") as fp:
        fp.write(json.dumps(final, sort_keys=True, indent=4))



#-----------Main Function Call----------#
if __name__ == "__main__":
    args = parse_command_line().parse_args()
    main(args)
