from flash.python_tool_kit.IOToolKit import IOToolKit
from flash.order_book.OrderProcessing import OrderBook,OrderHandler
import os
import sys



trade_flow_location=r"/Users/krzysiekbienias/Documents/GitHub/OrderBook/io/STREAM_FILES"
orders_sequence_file="match_due_to_sell.in"

output_stdout=r"/Users/krzysiekbienias/Documents/GitHub/OrderBook/io/OUTPUT_FILES"
output_names="out_11.out"

orders_gate_map=IOToolKit.parseInputFile(os.path.join(trade_flow_location,orders_sequence_file))

f=open(os.path.join(output_stdout,output_names),"w")
sys.stdout=f
OrderBook(incoming_orders=orders_gate_map)
print("THE END!")
f.close()


    

