from src.python_tool_kit.IOToolKit import IOToolKit
from src.order_book.OrderProcessing import OrderBook,OrderHandler
import os



trade_flow_location=r"/Users/krzysiekbienias/Documents/GitHub/OrderBook/io"
orders_sequence_file="test2.in"
# upload_orders=True
# process_order=False


orders_gate_map=IOToolKit.parseInputFile(os.path.join(trade_flow_location,orders_sequence_file))

OrderBook(incoming_orders=orders_gate_map)
    

