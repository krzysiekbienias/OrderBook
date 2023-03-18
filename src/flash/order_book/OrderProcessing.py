from python_tool_kit.IOToolKit import IOToolKit
from typing import TypeVar, Iterable, Tuple, Dict, List
import os
import heapq as h

HM = TypeVar("HM", bound=Dict)


class OrderHandler():

    def __init__(self,signal:HM) -> None:

        self._signal=signal

        self.type = None
        self.direction = None
        self.id = None
        self.price = None
        self.quantity = None
        self.peak = None

        self.unpackRequest(signal=self._signal)

        self.order_label = self.orderToDisplay()

    def unpackRequest(self, signal: str):

        self.type = signal['type']
        self.direction = signal["order"]['direction']
        self.id = signal["order"]['id']
        self.price = signal["order"]['price']
        self.quantity = signal["order"]["quantity"]
        if signal['type'] == "Iceberg":
            self._peak = signal["order"]['peak']
        return self
    
    def __lt__(self, other)->bool:
        """__lt__
        Description
        -----------
        This method compare two 'OrderHandler' objects and identify which is a  smaller one in terms of quantity.

        Parameters
        ----------
        other : OrderHandler
            

        Returns
        -------
        bool
            
        """
        return self.quantity < other.quantity
    
    def __gt__(self,other)->bool:
        """__gt__
        Description
        -----------
        This method compare two 'OrderHandler' objects and identify which is a larger one in terms of quantity.

        Parameters
        ----------
        other : _type_
            _description_

        Returns
        -------
        bool
            _description_
        """
        return self.quantity > other.quantity
    
    def __sub__(self,other):

        signal={"type":self.type,"order":{"direction":self.direction,"id":self.id,"price":self.price,"quantity":self.quantity-other.quantity}}
        return self.__class__(signal)



    
    def orderToDisplay(self)->HM:

        return {
            "id": self.id,
            "price": self.price,
            "quantity": self.quantity
        }
    
    def __str__(self) -> str:
        """__str__
        Description
        -----------
        String representation of 'OrderHandler' Object.

        Returns
        -------
        str
            _description_
        """
        return f'Order direction is {self.direction}. Order has following attributes: id:{self.id}, price:{self.price}, quantity:{self.quantity}'

class OrderBook:

    def __init__(self, incoming_orders: HM) -> None:

        self._incoming_orders = incoming_orders

        
        self.asks_list = []
        self.bids_list = []
        self.current_ask = None
        self.current_bid = None
        self._orders_status={"buyOrders":[],"sellOrders":[]}

        for incoming_order in incoming_orders.values():
            _order=OrderHandler(incoming_order)
            self.validateQuery(incoming_order=_order)
            self.incomingOrderHandle(order=_order)
            if not self.asks_list or not self.bids_list:
                self.toStdOut(order=_order)
            elif self.asks_list and self.bids_list:
                self.updateOrderBookCondition(incoming_order=_order)
               

                
    def incomingOrderHandle(self, order:OrderHandler)->None:
        """incomingOrderHandle
        Description
        -----------
        This method updates on fly the containers for asks and bids offers. It takes new offer and if this is a 'buy' offer then it puts on the heap,
        otherwise it puts on mean heap.

        Parameters
        ----------
        order : OrderHandler
            New order which is passing through a gate.
        """
        if order.direction == "Buy":
            h.heappush(self.asks_list,(-order.price,order))
        if order.direction == "Sell":
            h.heappush(self.bids_list,(order.price,order))
            
    def toStdOut(self,order:OrderHandler):
        if order.direction=="Buy":
            self._orders_status["buyOrders"].append(order.order_label)
            print(self._orders_status)
        elif order.direction=="Sell":
            self._orders_status["sellOrders"].append(order.order_label)
            print(self._orders_status) 




    def validateQuery(self,incoming_order:OrderHandler):
        if incoming_order.type not in ["Iceberg", "Limit"]:
            raise ValueError(
                "Type of order might be only 'Iceberg' and 'Limit'.")
        print(f"Query {incoming_order.id} is valid!")

    def updateOrderBookCondition(self,incoming_order:OrderHandler):
        max_price,trade_object_asks=self.asks_list[0]
        min_price,trade_object_bids=self.bids_list[0]
        if incoming_order.direction=="Buy":
            if incoming_order.price<min_price:
                print(f"Not possible to match trade for upcoming buy order with id: {incoming_order.__str__()}")

            else:
                self.matchingEngine(incoming_order=incoming_order,matched_order=trade_object_bids)
        elif incoming_order.direction=="Sell":
            if incoming_order.price>abs(max_price):
                print(f"Not possible to match trade for upcoming buy order with id: {incoming_order.__str__()}")
                self.toStdOut(incoming_order)
            else:
                self.matchingEngine(incoming_order=incoming_order,matched_order=trade_object_asks)


            

    def removeOrder(self,existing_order:OrderHandler):
        """removeOrder
        Description
        -----------
        Remove the record from book after cancel out two trades.

        Parameters
        ----------
        existing_order : OrderHandler
            Order that has been associated with new Order and thus removed from book.
        Note
        ----
        This happen only if volume of two trades are the same.    
        """
        if existing_order.direction=="Buy":
            self._orders_status["buyOrders"].remove(existing_order)
        elif existing_order.direction=="Sell":
            self._orders_status["sellOrders"].remove(existing_order)

        


    def matchingEngine(self,incoming_order:OrderHandler,matched_order:OrderHandler):
        """matchingEngine
        Description
        -----------
        This function update trade if match on the market happen. If both quantities are equal then we wipe out matched order from the book.

        Parameters
        ----------
        incoming_order : OrderHandler
            New order which just arrived from client.
        matched_order : OrderHandler
            Order that already exists in the book and deal may happen with the new offer.
        """
        print("Incoming Order:")
        print(incoming_order.__str__())

        print("We are matching with order:")
        print(matched_order.__str__())

        print("Matching Order: "+ matched_order.__str__())
        if incoming_order<matched_order:
            updated_order={"id":matched_order.id,"price":matched_order.price,"quantity":matched_order.quantity-incoming_order.quantity}
            self.incomingOrderHandle(order=updated_order)
        elif incoming_order>matched_order:
            updated_order=incoming_order-matched_order
            print("After transactions we have trade: ")
            print(updated_order.__str__()) 
            self.incomingOrderHandle(order=updated_order)
            self.toStdOut(order=updated_order)  
        else:
            print("Incoming order and match order are canceled out! Remove order with id match_order.")
            self.removeOrder(matched_order)
            

        
        
