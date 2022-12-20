# Trading
Trading Bot allowing to simulate different trading strategies


## Installation
```
sudo pip3 install -r requirements.txt
pip3 install -r requirements.txt
```

## Usage 
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

```
usage: statistics.py [-h] [-l] -d DIRECTORY

options:
  -h, --help            show this help message and exit
  -l, --logging         enable logging in the console

required arguments:
  -d DIRECTORY, --directory DIRECTORY
                        directory that contains results from previous tests
```

### strategy_validation.py
This script allows to validate simulated trading strategies with fixed parameters on all crypto currencies

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

### exceptional_list_creation.py
This script allows to extract the strategies that were the most efficient per crypto currency (for a specified period of time)

```
usage: exceptional_list_creation.py [-h] [-l] -d DIRECTORY

options:
  -h, --help            show this help message and exit
  -l, --logging         enable logging in the console

required arguments:
  -d DIRECTORY, --directory DIRECTORY
                        directory that contains results from previous tests
```
