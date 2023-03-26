# Order Book

## Preview.
In the trading world, the order book is the place where all active orders (both Bou and Sell) are maintained in certain priority for the purpose of matching buy and sell orders. Orders can be different types, but within this framework consider two following types:

* Limit Order  
A limit order is an order to buy or sell an asset that must be matched at a specified price or better.
* Iceberg Order  
An Iceberg order is a large single order that have been divided into smaller `limit orders`. This type of orders contains additional attribute `peak` that determines how much units the client wants to buy in one chunk.


#### Table of contents
[Installation and run](#installation)  
[Dependencies](#Dependencies)
[Project Structure](#ProjectStructure)  
[Dev Docs](#DevDocs)  
[General Overview](#GeneralOverview)  
[Configuration](#Configuration)  
[Further development](#Futherdevelopment)  


## Installation and run
After cloning the repository please kindly change root file in main for your local path where code has been deployed.
Then you may test different inputs by changing name of the test or define your own tests.

Then it might be run from bash using the command, permission to run granted.
```
./run.sh  main.py
```
Please only make sure that you are in main project's folder.
User must set working directory and pass name file in main.py file

```python
# ------------------
# Region: User customization
# ------------------ 
working_directory="/Users/krzysiekbienias/Documents/GitHub"
test_name="test1"
# ---------------------
# Region: User customization
# ---------------------
```

To upload list of trades a User must modify local path.

## Dependencies
Code has been developed and run using Python 3.11.
The project is run on its won python environment. It uses only basic python libraries
```python
import json
from typing import TypeVar, Iterable, Tuple, Dict, List
HM = TypeVar("HM", bound=Dict)
```
## Project Structure
Below we present structure of project `Flash`
```
-- io
    |--STREAM FILES
    |--OUTPUT FILES
-- src
    |-flash
    |    |--order_book
    |    |--python_tool_kit
    |-main.py
--README.md
--run.sh  
--.gitignore  
  
```

## Dev Docs
You may find html documentation class under following link

https://raw.githack.com/krzysiekbienias/order_book/master/docs/build/html/index.html

## General algorithm description
The hart of  this module is a matching engine, that handle the process of running deals within existing. Incoming order is handled on flay ad the deal is the fact peak has been chose to keep the efficiently way to match immediately the best offer for buy and sell. In case two or more orders with the same ask prices meet order that allow to run transaction with bid offer first is run deal with lower id.
After checking the matching then one more check is run to find out if re-balancing order book make possible for another deals.

Once trade goes through a gate the code sends to current status of order book. The second input, included in the same file is list of transactions if any happen.
## Input output format.
Input has following format.
```
{"type":"Limit","order":{"direction":"Buy","id":1,"price":14,"quantity":20}}
{"type":"Iceberg","order":{"direction":"Buy","id":2,"price":15,"quantity":50,"peak":20}}
{"type":"Limit","order":{"direction":"Sell","id":3,"price":16,"quantity":15}}
{"type":"Limit","order":{"direction":"Sell","id":4,"price":13,"quantity":60}}
```

Example of output format
```
{'buyOrders': [{'id': 1, 'price': 14, 'quantity': 20}], 'sellOrders': []}
{'buyOrders': [{'id': 1, 'price': 14, 'quantity': 20}, {'id': 2, 'price': 15, 'quantity': 50}], 'sellOrders': []}
{'buyOrders': [{'id': 1, 'price': 14, 'quantity': 20}, {'id': 2, 'price': 15, 'quantity': 50}], 'sellOrders': [{'id': 3, 'price': 16, 'quantity': 15}]}
{'buyOrders': [{'id': 1, 'price': 14, 'quantity': 10}], 'sellOrders': [{'id': 3, 'price': 16, 'quantity': 15}]}
{'buyOrderId': 2, 'sellOrderId': 4, 'price': 15, 'quantity': 20}
{'buyOrderId': 2, 'sellOrderId': 4, 'price': 15, 'quantity': 20}
{'buyOrderId': 2, 'sellOrderId': 4, 'price': 15, 'quantity': 10}
{'buyOrderId': 1, 'sellOrderId': 4, 'price': 13, 'quantity': 10}
```

## Further Development
* Implement class for generating random order book in form json that match input format file for extensive testing. 
* Implement Unit Tests
* Implement Jupyter lab as a demo.
* add logger files.



