# Order Book

## Preview,
In the trading world, the order book is the place where all active orders (both Bou and Sell) are maintained in certain priority for the purpose of matching buy and sell orders. Orders can be different types, but within this framework consider two following types:

* Limit Order  
A limit order is an order to buy or sell an asset that must be matched at a specified price or better.
* Iceberg Order  
An Iceberg order is a large single order that have been divided into smaller `limit orders`. This type of orders contains additional attribute `peak` that determines how much units the client wants to buy in one chunk.


#### Table of contents
[Installation](#installation)  
[Project Structure](#ProjectStructure)
[Dev Docs](#DevDocs)
[General Overview](#GeneralOverview)  
[Configuration](#Configuration)  

## Installation
## Project Structure
Below we present structure of project `Flash`
```
-- io
    |--STREAM FILES
    |--OUTPUT FILES
-- src
    |
  flash
    |--order_book
    |--python_tool_kit
```

## Dev Docs
You may find html documentation class under following link

https://raw.githack.com/krzysiekbienias/order_book/master/docs/build/html/index.html





