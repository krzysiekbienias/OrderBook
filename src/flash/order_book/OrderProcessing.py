from flash.python_tool_kit.IOToolKit import IOToolKit
from typing import TypeVar, Iterable, Tuple, Dict, List
import os
import heapq as h

HM = TypeVar("HM", bound=Dict)


class OrderHandler():

    def __init__(self, signal: HM) -> None:
        """__init__ 
        Description
        -----------
        Class that handles order object in abstract form.

        Parameters
        ----------
        signal : HM
            Single order that went through system's gate.
        """

        self._signal = signal

        self.type = None
        self.direction = None
        self.id = None
        self.price = None
        self.quantity = None
        self.peak = None

        self.unpackRequest(signal=self._signal)

        self.order_label = self.orderToDisplay()

    def unpackRequest(self, signal: str) -> None:
        """unpackRequest
        Description
        -----------
        Unpack trades' attributes from trade dictionary.

        Parameters
        ----------
        signal : str
            

        Returns
        -------
        None
        """

        self.type = signal['type']
        self.direction = signal["order"]['direction']
        self.id = signal["order"]['id']
        self.price = signal["order"]['price']
        self.quantity = signal["order"]["quantity"]
        if signal['type'] == "Iceberg":
            self._peak = signal["order"]['peak']
        return self

    def __lt__(self, other) -> bool:
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

    def __gt__(self, other) -> bool:
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

    def __sub__(self, other):
        """__sub__
        Description
        -----------
        This method defines how to subtract two orders in terms of quantities. In case of Iceberg order not define from quantity but from peak volume. 

        Parameters
        ----------
        other : OrderHandler
            Order to be subtract
        type : str, optional
            type, by default None

        Returns
        -------
        _type_
            _description_
        """
        if self.type == "Limit":
            signal = {
                "type": self.type,
                "order": {
                    "direction": self.direction,
                    "id": self.id,
                    "price": self.price,
                    "quantity": self.quantity - other.quantity
                }
            }
            return self.__class__(signal)
        elif self.type == "Iceberg":
            signal = {
                "type": self.type,
                "order": {
                    "direction": self.direction,
                    "id": self.id,
                    "price": self.price,
                    "quantity": self.peak - other.quantity
                }
            }
            return self.__class__(signal)

    def orderToDisplay(self) -> HM:
        """orderToDisplay
        This method casts trades parameters on hash map. 

        Returns
        -------
        HM
            HM required to display.
        """

        return {"id": self.id, "price": self.price, "quantity": self.quantity}

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
        """__init__
        Description
        -----------
        Class for processing new trade and set new trade status.

        Parameters
        ----------
        incoming_orders : HM
            Hash Map of hash maps that represents flow of trades.
        """

        self._incoming_orders = incoming_orders

        self.asks_list = []
        self.bids_list = []
        self._orders_status = {"buyOrders": [], "sellOrders": []}
        self._transactions_container = []

        for incoming_order in incoming_orders.values():
            _order = OrderHandler(incoming_order)
            self.validateQuery(incoming_order=_order)
            self.incomingOrderHandle(order=_order)
            if not self.asks_list or not self.bids_list:
                self.toStdOut(order=_order)
            elif self.asks_list and self.bids_list:
                self.updateOrderBookCondition(incoming_order=_order)

        if len(self._transactions_container) > 0:
            for tran in self._transactions_container:
                print(tran)

    def incomingOrderHandle(self, order: OrderHandler) -> None:
        """incomingOrderHandle
        Description
        -----------
        This method updates on fly the containers for asks and bids offers.
        It takes new offer and if this is a 'buy' offer then it puts on the heap,
        otherwise it puts on mean heap.

        Parameters
        ----------
        order : OrderHandler
            New order which is passing through a gate.
        """
        if order.direction == "Buy":
            h.heappush(self.asks_list, (-order.price, order))
        if order.direction == "Sell":
            h.heappush(self.bids_list, (order.price, order))

    def toStdOut(self, order: OrderHandler):
        """toStdOut
        Description
        -----------
        Display current state of the Order book.

        Parameters
        ----------
        order : OrderHandler
            Last order in system, which passed validation test.
        """
        if order.direction == "Buy":
            self._orders_status["buyOrders"].append(order.order_label)
            print(self._orders_status)
        elif order.direction == "Sell":
            self._orders_status["sellOrders"].append(order.order_label)
            print(self._orders_status)

    def validateQuery(self, incoming_order: OrderHandler):
        """validateQuery
        Description
        -----------
        This method check if order from stream is valid.

        Parameters
        ----------
        incoming_order : OrderHandler
            An order to be checked.

        Raises
        ------
        ValueError
            
        ValueError
            _description_
        ValueError
            _description_
        """
        if incoming_order.type not in ["Iceberg", "Limit"]:
            raise ValueError(
                "Type of order might be only 'Iceberg' and 'Limit'.")
        if incoming_order.price < 0:
            raise ValueError("Price cannot be negative!")
        if incoming_order.quantity < 0:
            raise ValueError("Quantity value cannot be negative!")
        if incoming_order.direction not in ["Buy", "Sell"]:
            raise ValueError("Direction might be only 'Buy' or 'Sell'")

        print(f"Query {incoming_order.id} is valid!")

    def updateOrderBookCondition(self, incoming_order: OrderHandler):

        max_price, trade_object_asks = self.asks_list[0]
        min_price, trade_object_bids = self.bids_list[0]
        if incoming_order.direction == "Buy":
            if incoming_order.price < min_price:
                print(
                    f"Not possible to match trade for upcoming buy order with id: {incoming_order.__str__()}"
                )

            else:
                self.matchingEngine(incoming_order=incoming_order,
                                    matched_order=trade_object_bids)
        elif incoming_order.direction == "Sell":
            if incoming_order.price > abs(max_price):
                print(
                    f"Not possible to match trade for upcoming buy order with id: {incoming_order.__str__()}"
                )
                self.toStdOut(incoming_order)
            else:
                self.matchingEngine(incoming_order=incoming_order,
                                    matched_order=trade_object_asks)

    def removeOrder(self, existing_order: OrderHandler):
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
        #TODO fix it!
        if existing_order.direction == "Buy":
            self._orders_status["buyOrders"].remove(existing_order.order_label)
        elif existing_order.direction == "Sell":
            self._orders_status["sellOrders"].remove(
                existing_order.order_label)

    def matchingEngine(self, incoming_order: OrderHandler,
                       matched_order: OrderHandler):
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

        print("Matching Order: " + matched_order.__str__())
        if incoming_order < matched_order:
            updated_order = matched_order - incoming_order
            print("After transactions we have trade: ")
            print(updated_order.__str__())
            if incoming_order.direction == "Sell" and matched_order.direction == "Buy":
                self.printTransactions(buy_order=matched_order,
                                       sell_order=incoming_order)
            else:
                self.printTransactions(buy_order=incoming_order,
                                       sell_order=matched_order)

            self.incomingOrderHandle(order=updated_order)
            self.removeOrder(matched_order)
            self.toStdOut(order=updated_order)

        elif incoming_order > matched_order:
            updated_order = incoming_order - matched_order
            print("After transactions we have trade: ")
            print(updated_order.__str__())
            self.incomingOrderHandle(order=updated_order)

            if incoming_order.direction == "Sell" and matched_order.direction == "Buy":
                self.printTransactions(buy_order=matched_order,
                                       sell_order=incoming_order)
            else:
                self.printTransactions(buy_order=incoming_order,
                                       sell_order=matched_order)
            self.removeOrder(matched_order)
            self.toStdOut(order=updated_order)
        else:
            print(
                "Incoming order and match order are canceled out! Remove order with id match_order."
            )
            if incoming_order.direction == "Sell" and matched_order.direction == "Buy":
                self.printTransactions(buy_order=matched_order,
                                       sell_order=incoming_order)
            else:
                self.printTransactions(buy_order=incoming_order,
                                       sell_order=matched_order)
            self.removeOrder(matched_order)

    def printTransactions(self, buy_order: OrderHandler,
                          sell_order: OrderHandler):

        if buy_order < sell_order:
            price = buy_order.price
            self._transactions_container.append({
                "buyOrderId": buy_order.id,
                "sellOrderId": sell_order.id,
                "price": price,
                "quantity": buy_order.quantity
            })
        elif buy_order > sell_order:
            price = sell_order.price
            self._transactions_container.append({
                "buyOrderId": buy_order.id,
                "sellOrderId": sell_order.id,
                "price": price,
                "quantity": sell_order.quantity
            })
