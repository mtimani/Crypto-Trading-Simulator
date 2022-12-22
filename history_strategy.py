#!/usr/bin/python3


#----------------Imports----------------#
import pandas as pd
import ta
import json
import sys
import argparse
import os
import os.path
import datetime
import numpy as np
from pygments import highlight 
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.lexers.web import JsonLexer
from termcolor import colored, cprint
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from binance import Client
from binance.exceptions import NotImplementedException, BinanceAPIException



#-------Initialize binance Client-------#
client = Client()



#-----------Global variables------------#
max_nb_strategies = 3
max_allowed_year = int(datetime.date.today().strftime("%Y"))
exceptional_old = {}
exceptional_new = {}



#---------Get data from Binance---------#
def getData(symbol, start, end):
    ## Variable initialization
    global max_allowed_year
    end_year = int(end.split("-")[0])

    ## Request to binance
    if end_year > max_allowed_year:
        frame = pd.DataFrame(client.get_historical_klines(symbol, '4h', start))
    else:
        frame = pd.DataFrame(client.get_historical_klines(symbol, '4h', start, end))

    frame = frame[[0,1,2,3,4]]
    frame.columns = ['Date','Open','High','Low','Close']
    frame.Date = pd.to_datetime(frame.Date, unit='ms')
    frame.set_index('Date', inplace=True)
    frame = frame.astype(float)
    return frame



#-------------Trading class-------------#
class DataTrader(Strategy):
    loss = 3
    window_1 = 100
    window_2 = 200
    strat = 1

    def init(self):
        close = self.data.Close
        self.macd = self.I(ta.trend.macd, pd.Series(close))
        self.macd_signal = self.I(ta.trend.macd_signal, pd.Series(close))
        self.ema_1 = self.I(ta.trend.ema_indicator, pd.Series(close), window=self.window_1)
        self.ema_2 = self.I(ta.trend.ema_indicator, pd.Series(close), window=self.window_2)
        self.sl_p = 1 - (self.loss / 10)
        self.tp_p = 1 + 1.5 * (self.loss / 10)
        self.sl = 0
        self.tp = 0

    def next(self):
        price = self.data.Close

        self.sl = price * self.sl_p
        self.tp = price * self.tp_p

        if self.strat == "1":
            if crossover(self.macd, self.macd_signal) and price < self.ema_1:
                self.buy(sl = self.sl, tp = self.tp)
            elif crossover(self.macd, self.macd_signal) and price > self.ema_1:
                self.sell(sl = self.tp, tp = self.sl)
        elif self.strat == "2":
            if crossover(self.macd, self.macd_signal) and price > self.ema_1:
                self.buy(sl = self.sl, tp = self.tp)
            elif crossover(self.macd, self.macd_signal) and price < self.ema_1:
                self.sell(sl = self.tp, tp = self.sl)
        elif self.strat == "3":
            if crossover(self.macd, self.macd_signal) and price > self.ema_1 and self.ema_1 > self.ema_2:
                self.buy(sl = self.sl, tp = self.tp)
            elif crossover(self.macd, self.macd_signal) and price < self.ema_1 and self.ema_1 < self.ema_2:
                self.sell(sl = self.tp, tp = self.sl)



#--Worker running different strategies--#
def worker_f(directory, year, logging):
    ## Variable initialization
    results = {}

    global max_nb_strategies
    global exceptional_old
    global exceptional_new

    ## Variable init for average calculations
    sum_of_values = 0
    number_of_values = 0

    ## Startdate variable initialization
    startdate   = year + "-01-01"
    enddate     = str(int(year) + 1) + "-01-01"

    ## Loop through all coins present in the exceptional_old dictionary
    for coin, contents in exceptional_old.items():
        try:
            ### Variables
            sl_p = contents["sl"]
            tp_p = contents["tp"]
            loss = int(100 - contents["sl"] * 100)
            window = int(contents["ema_window"])
            strategy = contents["strategy"]

            ### Backtesting for specific coin
            df = getData(coin, startdate, enddate)

            bt = Backtest(df, DataTrader, cash = 100000, commission = 0.0015)
            
            with np.errstate(invalid='ignore'):
                output = bt.optimize(loss=[loss],window_1=[window], strat=[strategy])

            ### Store results
            results[coin] = {"sl": sl_p, "tp": tp_p, "ema_window": window, "strategy": strategy, "return": output['Return [%]']}

            ### Average calculations
            sum_of_values += output['Return [%]']
            number_of_values += 1

            ### Exceptional values calculation
            if output['Return [%]'] > 100:
                exceptional_new[coin] = {"sl": sl_p, "tp": tp_p, "ema_window": window, "coin": coin, "strategy": strategy, "average": output['Return [%]']}
                
        except BinanceAPIException as e:
            ### Warning output to console if logging is enabled
            if logging:
                cprint("[WARNING]\tCoin " + coin + " is not available with sl = " + str(sl_p) + ", tp = " + str(tp_p) + ", window = " + str(window) + " and strategy = " + strategy + " for the year " + year, 'yellow')
            continue

        except KeyError:
            ### Warning output to console if logging is enabled
            if logging:
                cprint("[WARNING]\tCoin " + coin + " is not available with sl = " + str(sl_p) + ", tp = " + str(tp_p) + ", window = " + str(window) + " and strategy = " + strategy + " for the year " + year, 'yellow')
            continue

        except:
            ### Error output to console
            cprint('[ERROR]\t\tAn error occured for ' + coin + ' with sl = ' + str(sl_p) + ', tp = ' + str(tp_p) + ', window = ' + str(window) + ' and strategy = ' + strategy + " for the year " + year, 'red')
            continue

    ## Average calculation
    average = sum_of_values / number_of_values

    ## Final json formatting
    final = {"average": average, "results": results}
    formatted_final = json.dumps(final, indent=4)

    ## Write into output directory
    output_dir = directory + "/History_strategy/" + year + "/"
    output_file = output_dir + "optimized_out.json"
    
    with open(output_file, "w") as fp:
        fp.write(formatted_final)
    
    ## Display completion of the worker
    cprint("[INFO]\t\tSimulation of history strategy is complete for the year " + year, 'blue')

    ## Display to console if the logging is on
    if logging:
        colorful = highlight(formatted_final, lexer=JsonLexer(), formatter=Terminal256Formatter())
        print(colorful)



#--------Validate Year Parameter--------#
class validateYearParameter(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        global max_allowed_year

        if not (values.isnumeric()):
            parser.error(f"Please enter a valid year to test the history strategy (allowed values: from 2017 to " + str(max_allowed_year) + "). Got: " + values)
        else:
            if not(int(values) >= 2017 and int(values) <= max_allowed_year):
                parser.error(f"Please enter a valid year to test the history strategy (allowed values: from 2017 to " + str(max_allowed_year) + "). Got: " + values)
        setattr(namespace, self.dest, values)


            
#-----Validate Directory Parameter------#
class validateDirectoryParameter(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not os.path.isdir(values):
            parser.error(f"Please enter a valid directory to store results to. Got: {values}")
        else:
            if not(os.path.isfile(values + "/Exceptional_combination/exceptional_final.json")):
                parser.error(f"Please enter a valid directory that contains results from previous tests. Got: {values}")
        setattr(namespace, self.dest, values)
    


#--------Arguments Parse Function-------#
def parse_command_line():
    ## Global variables
    global max_allowed_year

    ## Arguments groups
    parser      = argparse.ArgumentParser()
    required    = parser.add_argument_group('required arguments')

    ## Arguments
    parser.add_argument("-l", "--logging", action='store_true', dest="logging", help="enable logging in the console")
    parser.add_argument("-y", "--year", dest="year", help="specify the year to test the history strategy (allowed values: from 2017 to " + str(max_allowed_year) + ")", required=False, default=max_allowed_year, action=validateYearParameter)
    required.add_argument("-d", "--directory", dest="directory", help="directory that will store results", required=True, action=validateDirectoryParameter)
    return parser



#-------------Main Function-------------#
def main(args):
    ## Variables
    directory   = args.directory
    logging     = args.logging
    year        = args.year
    
    global exceptional_old
    global exceptional_new

    ## Output to console if logging is enabled
    cprint("\n[INFO]\t\tRunning history_strategy.py test for the year " + year, 'blue')

    ## Create output directories
    try:
        os.mkdir(directory + "/History_strategy/")
        if logging:
            cprint("[INFO]\t\tCreation of " + directory + "/History_strategy/ directory", 'blue')
    except FileExistsError:
        if logging:
            cprint("[INFO]\t\tDirectory " + directory + "/History_strategy/ already exists", 'blue')
        else:
            None
    except:
        raise

    try:
        os.mkdir(directory + "/History_strategy/" + year)
        if logging:
            cprint("[INFO]\t\tCreation of " + directory + "/History_strategy/" + year + " directory", 'blue')
    except FileExistsError:
        if logging:
            cprint("[INFO]\t\tDirectory " + directory + "/History_strategy/" + year + " already exists", 'blue')
        else:
            None
    except:
        raise

    ## Populate exceptional_old dictionary
    with open(directory + "/Exceptional_combination/exceptional_final.json", "r") as fp:
        exceptional_old = json.load(fp)

        if logging:
            cprint("[INFO]\t\tContents of exceptional_final.json file loaded successfully", 'blue')

    ## Launch worker function
    worker_f(directory, year, logging)

    ## Write exceptional to file
    output_file = directory + "/History_strategy/History_strategy/" + year + "/exceptional.json"
    with open(output_file, "w") as fp:
        fp.write(json.dumps(exceptional_new, indent=4))



#-----------Main Function Call----------#
if __name__ == "__main__":
    args = parse_command_line().parse_args()
    main(args)
