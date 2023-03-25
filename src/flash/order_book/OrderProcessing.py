from flash.python_tool_kit.IOToolKit import IOToolKit
from typing import TypeVar, Iterable, Tuple, Dict, List
import os
import heapq as h
from collections import deque 

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
            self.peak = signal["order"]['peak']
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

    

    def orderToDisplay(self) -> HM:
        """orderToDisplay
        This method casts trades parameters on hash map. 

        Returns
        -------
        HM
            HM required to display.
        """

        return {"id": self.id, "price": self.price, "quantity": self.quantity}

    def updateQuantity(self, sub_quantity: int):
        """updateQuantity
        This function downgrades quantity volume after making a deal.

        Parameters
        ----------
        sub_quantity : int
        Quantity to be subtracted.
            

        Returns
        -------
        OrderHandler
            Object with update quantity.
        """
        if self.type == "Iceberg":
            signal = {
                "type": self.type,
                "order": {
                    "direction": self.direction,
                    "id": self.id,
                    "price": self.price,
                    "quantity": self.quantity - sub_quantity,
                    "peak":self.peak
                }
            }
            
        elif self.type == "Limit":
            signal = {
                "type": self.type,
                "order": {
                    "direction": self.direction,
                    "id": self.id,
                    "price": self.price,
                    "quantity": self.quantity - sub_quantity
                }
            }

        return self.__class__(signal)

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
        if self.type == "Limit":
            return f'Order type is "{self.type}". Order direction is "{self.direction}". This order has following attributes: id:{self.id}, price:{self.price}, quantity:{self.quantity}'
        else:
            return f'Order type is "{self.type}". Order direction is "{self.direction}" . This order has following attributes: id:{self.id}, price:{self.price}, quantity:{self.quantity}, peak:{self.peak}'


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

        # ------------------
        # Region: Class members
        # ------------------ 

        for incoming_order in incoming_orders.values():
            _order = OrderHandler(incoming_order)
            self.validateQuery(incoming_order=_order)
            self.flowOrderHandle(order=_order)
            if not self.asks_list or not self.bids_list:
                self.uploadToOrderStatus(order=_order)
            elif self.asks_list and self.bids_list:
               #overwritten_order is an existing order that we would have positive quantity after matching
               self.updateOrderBookCondition(incoming_order=_order)

        while len(self.asks_list)>0 and len(self.bids_list)>0:
            max_price,order_id_ask, trade_object_asks = self.asks_list[0]
            min_price,order_id_bid, trade_object_bids = self.bids_list[0]
            if abs(max_price)>=min_price:

                self.matchingEngine(trade_object_asks,trade_object_bids)
            else:
                break 


        print(self._orders_status)
        if len(self._transactions_container) > 0:
            for tran in self._transactions_container:
                print(tran)
        # ------------------
        # End Region: Class members
        # ------------------         

    # ------------------
    # Region: Order check
    # ------------------                
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
    # ------------------
    # End Region: Order check
    # ------------------            

    def flowOrderHandle(self, order: OrderHandler) -> None:
        """flowOrderHandle
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
            
            if any(order.id in sub_tuple for sub_tuple in self.asks_list):
                print("This trade already exist.")
                for _o in self.asks_list:
                    if _o[1]==order.id and order.quantity!=0:
                        _o[2].quantity=order.quantity
                    elif _o[1]==order.id and order.quantity==0:
                        self.asks_list.remove(_o)
                        

            else:
                #new order only push on peak
                h.heappush(self.asks_list, (-order.price,order.id, order))   
            # check if this trade, identified by od already exists in heap.
            #  If so then first remove it and then put on heap with updated quantity.
        if order.direction == "Sell":
            if any(order.id in sub_tuple for sub_tuple in self.bids_list):
                print("This trade already exist.")
                for _o in self.bids_list:
                    if _o[1]==order.id and order.quantity!=0:
                        _o[2].quantity=order.quantity
                    elif _o[1]==order.id and order.quantity==0:
                        self.bids_list.remove(_o)
                

            # check if this trade, identified by od already exists in heap.
            #  If so then first remove it and then put on heap with updated quantity.
            else:
                #new order only push on peak
                h.heappush(self.bids_list, (order.price,order.id, order))

    def uploadToOrderStatus(self, order: OrderHandler):
        """uploadToOrderStatus
        Description
        -----------
        Upload new order for the Order book.

        Parameters
        ----------
        order : OrderHandler
            Last order in system, which passed validation test.
        """
        if len(self._orders_status["sellOrders"])==0 or len(self._orders_status["buyOrders"])==0:
            if order.direction == "Buy" :
                    self._orders_status["buyOrders"].append(order.order_label)
            elif order.direction == "Sell":
                    self._orders_status["sellOrders"].append(order.order_label)        
        ids_in_order_book=[]
        for ex_order in self._orders_status["buyOrders"]+self._orders_status["sellOrders"]:
            ids_in_order_book.append(ex_order["id"])
        if order.id not in ids_in_order_book:
            if order.direction == "Buy" :
                self._orders_status["buyOrders"].append(order.order_label)
                
            elif order.direction == "Sell":
                self._orders_status["sellOrders"].append(order.order_label)
        else:
            for ex_order in self._orders_status["buyOrders"]+self._orders_status["sellOrders"]:
                if  ex_order["id"]==order.id and ex_order["quantity"]!=order.quantity: 
                    if order.direction == "Buy":
                        ex_order["quantity"]=order.quantity
                    elif order.direction == "Sell":
                        ex_order["quantity"]=order.quantity
                else:
                    continue



     


    def updateOrderBookCondition(self, incoming_order: OrderHandler):
        """updateOrderBookCondition
        Description
        -----------


        Parameters
        ----------
        incoming_order : OrderHandler
            _description_
        """
        
        max_price,order_id, trade_object_asks = self.asks_list[0]
        min_price,order_id, trade_object_bids = self.bids_list[0]
        
        if incoming_order.direction == "Buy":
            if incoming_order.price < min_price:
                print(
                    f"Not possible to match trade for upcoming buy order with id: {incoming_order.__str__()}"
                )
                self.uploadToOrderStatus(incoming_order)

            else:
                 
                   return self.matchingEngine(incoming_order=incoming_order,
                                        matched_order=trade_object_bids)
        elif incoming_order.direction == "Sell":
            if incoming_order.price > abs(max_price):
                print(
                    f"Not possible to match trade for upcoming buy order with id: {incoming_order.__str__()}"
                )
                self.uploadToOrderStatus(incoming_order)
            else: 
                
                    return self.matchingEngine(incoming_order=incoming_order,
                                               matched_order=trade_object_asks)

    def removeOrder(self, existing_order: OrderHandler,id_for_remove:int):
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
        
        for order in self._orders_status["buyOrders"]+self._orders_status["sellOrders"]:
            if order["id"]==id_for_remove and existing_order.direction == "Buy":
                self._orders_status["buyOrders"].remove(order)
            elif order["id"]==id_for_remove and existing_order.direction == "Sell":
                    self._orders_status["sellOrders"].remove(order)



    def matchingEngine(self,
                        incoming_order: OrderHandler,
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
        # ------------------
        # Region: Two Limits Order
        # ------------------
        if incoming_order.type == "Limit" and matched_order.type == "Limit":
            print("We are matching limit orders ...")
            
            if incoming_order < matched_order: #here we compare quantity
                # ------------------
                # Region: Incoming Order has bigger volume
                # ------------------
                
                incoming_order_after_deal=incoming_order.updateQuantity(incoming_order.quantity)
                matched_order_after_deal=matched_order.updateQuantity(incoming_order.quantity)
                if incoming_order.direction == "Sell" and matched_order.direction == "Buy":
                    self.uploadTransactions(buy_order=matched_order,
                                            sell_order=incoming_order)
                else:
                    self.uploadTransactions(buy_order=incoming_order,
                                            sell_order=matched_order)
                if incoming_order_after_deal.quantity==0:  
                    
                    self.flowOrderHandle(order=incoming_order_after_deal)
                    self.flowOrderHandle(order=matched_order_after_deal)
                    
                    self.uploadToOrderStatus(order=matched_order_after_deal)
                    self.removeOrder(existing_order=incoming_order,id_for_remove=incoming_order.id)
                    # we need to check order status and in case when quantity after matching is equal zero.
                    # There is no need to display this but must be removed. 
                    

                else:
                    self.flowOrderHandle(order=incoming_order_after_deal)
                    self.flowOrderHandle(order=matched_order_after_deal)
                

             
                # ------------------
                # End Region: Incoming Order has bigger volume
                # ------------------
            elif incoming_order > matched_order:
            # ------------------
            # Region: Existing Order has bigger volume
            # ------------------

                # we compare with respect to quantity so we subtract quantity from smaller
    
                
                incoming_order_after_deal=incoming_order.updateQuantity(matched_order.quantity)
                matched_order_after_deal=matched_order.updateQuantity(matched_order.quantity)
                if incoming_order.direction == "Sell" and matched_order.direction == "Buy":
                    self.uploadTransactions(buy_order=matched_order,
                                            sell_order=incoming_order)
                else:
                    self.uploadTransactions(buy_order=incoming_order,
                                            sell_order=matched_order)
                
                if matched_order_after_deal.quantity==0:  
                    #update heap for both and in addition remove from status book existing order. There is no volume
                    
                    self.flowOrderHandle(order=matched_order_after_deal)
                    self.flowOrderHandle(order=incoming_order_after_deal)
                    self.uploadToOrderStatus(order=incoming_order_after_deal)
                    self.removeOrder(existing_order=matched_order,id_for_remove=matched_order.id)
                    
                    

                else:

                    self.flowOrderHandle(order=incoming_order_after_deal)
                    self.flowOrderHandle(order=matched_order_after_deal)
            # ------------------
            # End Region: Existing Order has bigger volume
            # ------------------        
                    
            else:
            # ------------------
            # Region: Order volumes are equal
            # ------------------


                print(
                    "Incoming order and match order are canceled out! Remove order with id match_order."
                )
                incoming_order_after_deal=incoming_order.updateQuantity(incoming_order.quantity)
                matched_order_after_deal=matched_order.updateQuantity(incoming_order.quantity)
                if incoming_order.direction == "Sell" and matched_order.direction == "Buy":
                    self.uploadTransactions(buy_order=matched_order,
                                            sell_order=incoming_order)
                else:
                    self.uploadTransactions(buy_order=incoming_order,
                                            sell_order=matched_order)
                self.flowOrderHandle(order=matched_order_after_deal)
                self.flowOrderHandle(order=incoming_order_after_deal)    
                self.uploadToOrderStatus(order=incoming_order_after_deal)
                self.uploadToOrderStatus(order=matched_order_after_deal)
                self.removeOrder(existing_order=matched_order,id_for_remove=matched_order.id)
                self.removeOrder(existing_order=incoming_order,id_for_remove=incoming_order.id)
            # ------------------
            # Region: Order volumes are equal
            # ------------------          
                
        
        
        # ------------------
        # End Region: Two Limits Order
        # ------------------
        else:
        # ------------------
        # Region: Iceberg Order
        # ------------------
            outstanding_quantity = min(incoming_order.quantity,
                                       matched_order.quantity)
            if incoming_order.peak is not None:
                peak = incoming_order.peak
            elif matched_order.peak is not None:
                peak = incoming_order.peak

                if (incoming_order.type == "Iceberg"
                        or matched_order.type == "Iceberg"):
                    print("At least one order is an Iceberg order...")

                    if incoming_order < matched_order:
                        while outstanding_quantity > 0:
                            updated_order = matched_order - incoming_order
                            if incoming_order.direction == "Sell" and matched_order.direction == "Buy":
                                self.uploadTransactions(
                                    buy_order=matched_order,
                                    sell_order=incoming_order)
                                print(self._transactions_container)
                            else:
                                self.uploadTransactions(
                                    buy_order=incoming_order,
                                    sell_order=matched_order)
                            print("After transactions we have trade: ")
                            print(updated_order.__str__())
                        self.flowOrderHandle(order=updated_order)
                        self.removeOrder(matched_order)
                        self.uploadToOrderStatus(order=updated_order)

                    elif incoming_order > matched_order:

                        #do until smaller order quantity ois positive
                        while matched_order.quantity > 0:
                            if incoming_order.type == "Limit" and matched_order.type == "Iceberg":
                                if incoming_order.direction == "Sell" and matched_order.direction == "Buy":
                                    self.uploadTransactions(buy_order=matched_order,sell_order=incoming_order)
                                    print(self._transactions_container)
                                else:
                                    self.uploadTransactions(buy_order=incoming_order,sell_order=matched_order)
                                    print(self._transactions_container)

                                if matched_order.quantity>=matched_order.peak:
                                    incoming_order=incoming_order.updateQuantity(matched_order.peak)
                                    matched_order=matched_order.updateQuantity(matched_order.peak)
                                else:
                                    incoming_order=incoming_order.updateQuantity(matched_order.quantity)
                                    matched_order=matched_order.updateQuantity(matched_order.quantity)

                                print(str(incoming_order))
                                print(str(matched_order))
                            elif incoming_order.type == "Iceberg" and matched_order.type == "Limit":
                                if incoming_order.direction == "Sell" and matched_order.direction == "Buy":
                                    self.uploadTransactions(buy_order=matched_order,sell_order=incoming_order)
                                    print(self._transactions_container)
                                else:
                                    self.uploadTransactions(buy_order=incoming_order,sell_order=matched_order)
                                    print(self._transactions_container)    

                                if incoming_order.quantity>=incoming_order.peak:
                                    incoming_order=incoming_order.updateQuantity(incoming_order.peak)
                                    matched_order=matched_order.updateQuantity(incoming_order.peak)
                                else:
                                    incoming_order=incoming_order.updateQuantity(incoming_order.quantity)
                                    matched_order=matched_order.updateQuantity(incoming_order.quantity)    
                                print(str(incoming_order))
                                print(str(matched_order))

                        updated_order=incoming_order #always order for which still quantity is positive    
                        self.flowOrderHandle(order=updated_order)
                        id_order_to_remove=matched_order.id
                        self.removeOrder(matched_order,id_for_remove=id_order_to_remove)
                        h.heappop(self.asks_list)
                        return updated_order

                        #remove must be done via id, because trade's attributes might be modified 
                        #before prompt this check if another match is possible, so remove prompter
                        # ------------------
                        #  End Region: Iceberg Order
                        # ------------------
                      

    def uploadTransactions(self, buy_order: OrderHandler,
                           sell_order: OrderHandler):
        """uploadTransactions
        Description
        -----------
        This method prints transactions that has place in format defined in the spec. 

        Parameters
        ----------
        buy_order : OrderHandler
            Matching order from ask side.
        sell_order : OrderHandler
            Matching order from bid side.
        """

        if buy_order < sell_order:
            price = buy_order.price
            if buy_order.type == "Limit":
                self._transactions_container.append({
                    "buyOrderId":
                    buy_order.id,
                    "sellOrderId":
                    sell_order.id,
                    "price":
                    price,
                    "quantity":
                    buy_order.quantity
                })
            elif buy_order.type == "Iceberg":
                if buy_order.quantity>=buy_order.peak:
                    self._transactions_container.append({
                        "buyOrderId": buy_order.id,
                        "sellOrderId": sell_order.id,
                        "price": price,
                        "quantity": buy_order.peak
                    })
                else:
                    self._transactions_container.append({
                        "buyOrderId": buy_order.id,
                        "sellOrderId": sell_order.id,
                        "price": price,
                        "quantity": buy_order.quantity
                    })


        elif buy_order > sell_order:
            price = sell_order.price
            if sell_order.type == "Limit":
                self._transactions_container.append({
                    "buyOrderId":
                    buy_order.id,
                    "sellOrderId":
                    sell_order.id,
                    "price":
                    price,
                    "quantity":
                    sell_order.quantity
                })
            elif sell_order.type == "Iceberg":
                if sell_order.quantity>=sell_order.peak:
                    self._transactions_container.append({
                        "buyOrderId": buy_order.id,
                        "sellOrderId": sell_order.id,
                        "price": price,
                        "quantity": sell_order.peak
                    })
                else:
                      self._transactions_container.append({
                        "buyOrderId": buy_order.id,
                        "sellOrderId": sell_order.id,
                        "price": price,
                        "quantity": sell_order.quantity
                    })
        else:
            price = sell_order.price
            if sell_order.type == "Limit":
                self._transactions_container.append({
                    "buyOrderId":
                    buy_order.id,
                    "sellOrderId":
                    sell_order.id,
                    "price":
                    price,
                    "quantity":
                    sell_order.quantity
                })
            elif sell_order.type == "Iceberg":
                if sell_order.quantity>=sell_order.peak:
                    self._transactions_container.append({
                        "buyOrderId": buy_order.id,
                        "sellOrderId": sell_order.id,
                        "price": price,
                        "quantity": sell_order.peak
                    })
                else:
                    self._transactions_container.append({
                        "buyOrderId": buy_order.id,
                        "sellOrderId": sell_order.id,
                        "price": price,
                        "quantity": sell_order.quantity
                    })  
                
