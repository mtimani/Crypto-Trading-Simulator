# Trading
Trading Bot allowing to simulate different trading strategies


## Installation
```
sudo pip3 install -r requirements.txt
pip3 install -r requirements.txt
```

## Automated launch with the launcher.py script
**This script allows to launch all the scripts allowing a full simulation of all available strategies**  

```
usage: launcher.py [-h] [-l] -d DIRECTORY (-a | -s STRATEGY [STRATEGY ...])

options:
  -h, --help            show this help message and exit
  -l, --logging         enable logging in the console

required arguments:
  -d DIRECTORY, --directory DIRECTORY
                        directory that contains results from previous tests

mutually exclusive arguments:
  -a, --all             run all scripts for all strategies
  -s STRATEGY [STRATEGY ...], --strategies STRATEGY [STRATEGY ...]
                        run specific strategies (allowed strategies between 1 and 3)
```

## Usage of each script separately
### strategy_testing.py
This script allows to simulate trading strategies with multiple parameters on all crypto currencies

```
usage: strategy_testing.py [-h] [-l] [-s STRATEGY] -d DIRECTORY

options:
  -h, --help            show this help message and exit
  -l, --logging         enable logging in the console
  -s STRATEGY, --strategy STRATEGY
                        choose strategy between 1 and 3 (default strategy: 1)

required arguments:
  -d DIRECTORY, --directory DIRECTORY
                        directory that will store results
```

### statistics.py
This script allows to find the most promicing parameters from tested trading strategies  
**The script must be ran only after the execution of the strategy_testing.py script is complete**

```
usage: statistics.py [-h] [-l] -d DIRECTORY (-a | -s STRATEGY [STRATEGY ...])

options:
  -h, --help            show this help message and exit
  -l, --logging         enable logging in the console

required arguments:
  -d DIRECTORY, --directory DIRECTORY
                        directory that contains results from previous tests

mutually exclusive arguments:
  -a, --all             run script with all strategies
  -s STRATEGY [STRATEGY ...], --strategies STRATEGY [STRATEGY ...]
                        run script with specific strategies (allowed strategies between 1 and 3)
```

### exceptional_list_creation.py
This script allows to extract the strategies that were the most efficient per crypto currency (for a specified period of time)  
**The script must be ran only after the execution of the strategy_testing.py script is complete**

```
usage: exceptional_list_creation.py [-h] [-l] -d DIRECTORY (-a | -s STRATEGY [STRATEGY ...])

options:
  -h, --help            show this help message and exit
  -l, --logging         enable logging in the console

required arguments:
  -d DIRECTORY, --directory DIRECTORY
                        directory that contains results from previous tests

mutually exclusive arguments:
  -a, --all             run script with all strategies
  -s STRATEGY [STRATEGY ...], --strategies STRATEGY [STRATEGY ...]
                        run script with specific strategies (allowed strategies between 1 and 3)
```

### strategy_validation.py
This script allows to validate simulated trading strategies with fixed parameters on all crypto currencies  
**The script can be ran after the execution of the strategy_testing.py script is complete (not mandatory)**  

```
usage: strategy_validation.py [-h] [-l] -d DIRECTORY [-s STRATEGY] -m MAX_LOSSES -e EMA_WINDOW

options:
  -h, --help            show this help message and exit
  -l, --logging         enable logging in the console

required arguments:
  -d DIRECTORY, --directory DIRECTORY
                        directory that will store results
  -s STRATEGY, --strategy STRATEGY
                        choose strategy between 1 and 3
  -m MAX_LOSSES, --max-losses MAX_LOSSES
                        maximum loss percentage accepted by the strategy (allowed values between 1 and 9)
  -e EMA_WINDOW, --ema-window EMA_WINDOW
                        EMA window size (allowed values: 20, 50, 100, 200)
```
