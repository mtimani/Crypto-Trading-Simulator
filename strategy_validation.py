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



#----------------Cryptos----------------#
#coins = ["ETHUSDT"]
coins = ["AAVEUSDT","ABBCUSDT","ADAUSDT","ALGOUSDT","AMPUSDT","ANKRUSDT","ANTUSDT","APEUSDT","APIUSDT","APTUSDT","ARUSDT","ASTRUSDT","ATOMUSDT","AUDIOUSDT","AVAXUSDT","AXSUSDT","BALUSDT","BATUSDT","BCHUSDT","BITUSDT","BNBUSDT","BNXUSDT","BONEUSDT","BORAUSDT","BSVUSDT","BTCUSDT","BTGUSDT","BTRSTUSDT","BTTUSDT","BUSDUSDT","CAKEUSDT","CELUSDT","CELOUSDT","CELRUSDT","CHRUSDT","CHSBUSDT","CHZUSDT","COMPUSDT","CROUSDT","CRVUSDT","CSPRUSDT","CVCUSDT","CVXUSDT","DAIUSDT","DAOUSDT","DASHUSDT","DCRUSDT","DGBUSDT","DOGEUSDT","DOTUSDT","DYDXUSDT","EGLDUSDT","ELONUSDT","ENJUSDT","ENSUSDT","EOSUSDT","ETCUSDT","ETHUSDT","ETHWUSDT","EWTUSDT","FEIUSDT","FILUSDT","FLOWUSDT","FLUXUSDT","FTMUSDT","FXSUSDT","GALAUSDT","GLMUSDT","GLMRUSDT","GMTUSDT","GMXUSDT","GNOUSDT","GRTUSDT","GTUSDT","GUSDUSDT","HBARUSDT","HIVEUSDT","HNTUSDT","HOTUSDT","HTUSDT","ICPUSDT","ICXUSDT","ILVUSDT","IMXUSDT","INJUSDT","IOSTUSDT","IOTXUSDT","JASMYUSDT","JSTUSDT","KAVAUSDT","KCSUSDT","KDAUSDT","KLAYUSDT","KNCUSDT","KSMUSDT","LDOUSDT","LEOUSDT","LINKUSDT","LPTUSDT","LRCUSDT","LSKUSDT","LTCUSDT","LUNAUSDT","LUNCUSDT","MAGICUSDT","MANAUSDT","MASKUSDT","MATICUSDT","MDXUSDT","MEDUSDT","METISUSDT","MINAUSDT","MIOTAUSDT","MKRUSDT","MXUSDT","MXCUSDT","NEARUSDT","NEOUSDT","NEXOUSDT","NFTUSDT","OCEANUSDT","OKBUSDT","OMGUSDT","ONEUSDT","ONGUSDT","ONTUSDT","OPUSDT","OSMOUSDT","PAXGUSDT","PEOPLEUSDT","PLAUSDT","POLYUSDT","PUNDIXUSDT","PYRUSDT","QNTUSDT","QTUMUSDT","RBNUSDT","REQUSDT","RLCUSDT","RNDRUSDT","ROSEUSDT","RSRUSDT","RUNEUSDT","RVNUSDT","SANDUSDT","SCUSDT","SCRTUSDT","SFPUSDT","SHIBUSDT","SKLUSDT","SLPUSDT","SNTUSDT","SNXUSDT","SOLUSDT","SSVUSDT","STORJUSDT","STXUSDT","SUSHIUSDT","SXPUSDT","SYSUSDT","TUSDT","TFUELUSDT","THETAUSDT","TONUSDT","TRIBEUSDT","TRXUSDT","TUSDUSDT","TWTUSDT","UMAUSDT","UNIUSDT","USDCUSDT","USDDUSDT","USDNUSDT","USDPUSDT","USDTUSDT","USTCUSDT","VETUSDT","VGXUSDT","WAVESUSDT","WAXPUSDT","WBTCUSDT","WINUSDT","WOOUSDT","XCHUSDT","XCNUSDT","XDCUSDT","XECUSDT","XEMUSDT","XLMUSDT","XMRUSDT","XNOUSDT","XRPUSDT","XTZUSDT","XYMUSDT","YFIUSDT","ZECUSDT","ZENUSDT","ZILUSDT","ZRXUSDT"]


#-----------Global variables------------#
strategy = 0
max_allowed_year = int(datetime.date.today().strftime("%Y"))
max_nb_strategies = 3
exceptional = {}



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
        global strategy
        self.strat = strategy

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
def worker_f(directory, strat, max_losses, ema_window, year, logging):
    ## Variable initialization
    results = {}

    global strategy
    strategy = strat 

    ## Startdate variable initialization
    startdate   = year + "-01-01"
    enddate     = str(int(year) + 1) + "-01-01"

    ## Variable init for average calculations
    sum_of_values = 0
    number_of_values = 0

    ## Execute strategy for all coins
    for coin in coins:
        try:
            ### Backtesting for specific coin
            df = getData(coin, startdate, enddate)
            bt = Backtest(df, DataTrader, cash = 100000, commission = 0.0015)
            with np.errstate(invalid='ignore'):
                output = bt.optimize(loss=[int(max_losses)],window_1=[int(ema_window)])

            loss = float(str(output._strategy).split('loss=')[1].split(',')[0]) / 100
            sl_p = float(str(round(1 - loss, 3)))
            tp_p = 1 + 1.5 * loss
            
            window = float(str(output._strategy).split('window_1=')[1].split(')')[0]) 

            ### Store results
            results[coin] = {"sl": sl_p, "tp": tp_p, "ema_window": window, "strategy": strategy, "return": output['Return [%]']}

            ### Average calculations
            sum_of_values += output['Return [%]']
            number_of_values += 1

            ### Exceptional values calculation
            if output['Return [%]'] > 100:
                exceptional[coin] = {"sl": sl_p, "tp": tp_p, "ema_window": window, "strategy": strategy, "average": output['Return [%]']}

        except BinanceAPIException as e:
            ### Warning output to console if logging is enabled
            if logging:
                cprint("[WARNING]\tCoin " + coin + " is not available with sl = " + str(sl_p) + ", tp = " + str(tp_p) + ", window = " + str(window) + " and year = " + year, 'yellow')
            continue

        except:
            ### Error output to console
            cprint('[ERROR]\t\tAn error occured for ' + coin + ' with sl = ' + str(sl_p) + ', tp = ' + str(tp_p) + ', window = ' + str(window) + ' and year = ' + year, 'red')
            continue

    ## Average calculation
    average = sum_of_values / number_of_values

    ## Final json formatting
    final = {"average": average, "results": results}
    formatted_final = json.dumps(final, indent=4)

    ## Write into output directory
    output_dir = directory + "/Strategy_validation/Strategy_" + strategy + "_validation/" + year + "/"
    output_file = output_dir + "optimized_out.json"
    
    with open(output_file, "w") as fp:
        fp.write(formatted_final)
    
    ## Display completion of the worker
    cprint("[INFO]\t\tSimulation of strategy " + strategy + " for the year " + year + " is complete", 'blue')

    ## Display to console if the logging is on
    if logging:
        colorful = highlight(formatted_final, lexer=JsonLexer(), formatter=Terminal256Formatter())
        print(colorful)



#--------Validate Year Parameter--------#
class validateYearParameter(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        global max_allowed_year

        if not (values.isnumeric()):
            parser.error(f"Please enter a valid year to validate the strategy (allowed values: from 2017 to " + str(max_allowed_year) + "). Got: " + values)
        else:
            if not(int(values) >= 2017 and int(values) <= max_allowed_year):
                parser.error(f"Please enter a valid year to validate the strategy (allowed values: from 2017 to " + str(max_allowed_year) + "). Got: " + values)
        setattr(namespace, self.dest, values)



#------Validate Strategy Parameter------#
class validateStrategyParameter(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        ## Global variables
        global max_nb_strategies

        allowed_values = []
        for i in range(1,max_nb_strategies+1):
            allowed_values.append(str(i))

        if not (values in allowed_values):
            parser.error(f"Please enter a valid strategy number (between 1 and " + str(max_nb_strategies) + "). Got: {values}")
        setattr(namespace, self.dest, values)



#-----Validate Directory Parameter------#
class validateDirectoryParameter(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not os.path.isdir(values):
            parser.error(f"Please enter a valid directory to store results to. Got: {values}")
        setattr(namespace, self.dest, values)



#----Validate Max Losses Parameter------#
class validateMaxLossesParameter(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        try:
            if float(values) < 1.0 or float(values) > 9.0:
                parser.error(f"Please enter a valid maximum loss percentage accepted by the strategy (allowed values between 1 and 9). Got: {values}")
        except ValueError:
            parser.error(f"Please enter a valid maximum loss percentage accepted by the strategy (allowed values between 1 and 9). Got: {values}")
        setattr(namespace, self.dest, values)



#----Validate Max Losses Parameter------#
class validateEMAWindowParameter(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        allowed_values = ["20","50","100","200"]
        if not (values in allowed_values):
            parser.error(f"Please enter a valid EMA window size (allowed values: 20, 50, 100, 200). Got: {values}")
        setattr(namespace, self.dest, values)



#--------Arguments Parse Function-------#
def parse_command_line():
    ## Global variables
    global max_nb_strategies
    global max_allowed_year

    ## Arguments groups
    parser      = argparse.ArgumentParser()
    required    = parser.add_argument_group('required arguments')

    ## Arguments
    parser.add_argument("-l", "--logging", action='store_true', dest="logging", help="enable logging in the console")
    parser.add_argument("-y", "--year", dest="year", help="specify the year to validate the strategy (allowed values: from 2017 to " + str(max_allowed_year) + ")", required=False, default=max_allowed_year, action=validateYearParameter)
    parser.add_argument("-s", "--strategy", dest="strategy", help="choose strategy between 1 and " + str(max_nb_strategies), required=False, action=validateStrategyParameter)
    required.add_argument("-d", "--directory", dest="directory", help="directory that will store results", required=True, action=validateDirectoryParameter)
    required.add_argument("-m", "--max-losses", dest="max_losses", help="maximum loss percentage accepted by the strategy (allowed values between 1 and 9)", required=True, action=validateMaxLossesParameter)
    required.add_argument("-e", "--ema-window", dest="ema_window", help="EMA window size (allowed values: 20, 50, 100, 200)", required=True, action=validateEMAWindowParameter)
    return parser



#-------------Main Function-------------#
def main(args):
    ## Variables
    directory   = args.directory
    logging     = args.logging
    strategy    = args.strategy
    max_losses  = args.max_losses
    ema_window  = args.ema_window
    year        = args.year

    ## Output to console if logging is enabled
    losses = str(round(1 - float(max_losses) / 100, 3))
    cprint("\n[INFO]\t\tRunning strategy_validation.py with the strategy number " + strategy + ", losses = " + losses + ", ema_window = " + ema_window + " and year = " + year, 'blue')

    ## Create output directories
    try:
        os.mkdir(directory + "/Strategy_validation")
        if logging:
            cprint("[INFO]\t\tCreation of " + directory + "/Strategy_validation directory", 'blue')
    except FileExistsError:
        if logging:
            cprint("[INFO]\t\tDirectory " + directory + "/Strategy_validation already exists", 'blue')
        else:
            None
    except:
        raise
    try:
        os.mkdir(directory + "/Strategy_validation/Strategy_" + strategy + "_validation")
        if logging:
            cprint("[INFO]\t\tCreation of " + directory + "/Strategy_validation/Strategy_" + strategy + "_validation directory", 'blue')
    except FileExistsError:
        if logging:
            cprint("[INFO]\t\tDirectory " + directory + "/Strategy_validation/Strategy_" + strategy + "_validation already exists", 'blue')
        else:
            None
    except:
        raise
    try:
        os.mkdir(directory + "/Strategy_validation/Strategy_" + strategy + "_validation/" + year)
        if logging:
            cprint("[INFO]\t\tCreation of " + directory + "/Strategy_validation/Strategy_" + strategy + "_validation/" + year + " directory", 'blue')
    except FileExistsError:
        if logging:
            cprint("[INFO]\t\tDirectory " + directory + "/Strategy_validation/Strategy_" + strategy + "_validation/" + year + " already exists", 'blue')
        else:
            None
    except:
        raise

    worker_f(directory, strategy, max_losses, ema_window, year, logging)

    ## Write exceptional to file
    output_file = directory + "/Strategy_validation/Strategy_" + strategy + "_validation/" + year + "/exceptional.json"
    with open(output_file, "w") as fp:
        fp.write(json.dumps(exceptional, indent=4))



#-----------Main Function Call----------#
if __name__ == "__main__":
    args = parse_command_line().parse_args()
    main(args)
