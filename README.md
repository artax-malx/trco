TRCO
=====

Tradesystem Cocoa (TRCO), system trading active cocoa futures on ICE

Note that all code has to be run from the root directory 

See presentation [cocoa\_trading\_system](docs/cocoa_trading_system) with a description of the methodology and the results.


### Requirements

Running `trco` requires:

* Python 3.12 (tested under Python 3.12.16)

### Installation
* Install all the required libraries using the requirements file:
```console
python3 -m pip install -r requirements.txt
```

### Running code
* Run tests from the root directory with command:
```console
python3 -m pytest tests
```
Note that the there is only a test template and no actual tests yet.

* Generate the active future time series first using:
```console
python3 make_price_series.py 
```
* After generating the active future time series, backtest trade system using [strategy.py](trco/strategy.py) 
```console
python3 trco/strategy.py 
```

* All input data is in the folder [data](data) and the outputs are also written to it

* When running the code a log folder is automatically created for the log files
