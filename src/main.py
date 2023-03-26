from flash.python_tool_kit.IOToolKit import IOToolKit
from flash.order_book.OrderProcessing import OrderBook,OrderHandler
import os
import sys


# ------------------
# Region: User customization
# ------------------ 
working_directory="/Users/krzysiekbienias/Documents/GitHub"
test_name="test1"
# ---------------------
# Region: User customization
# ---------------------

trade_flow_location="OrderBook/io/STREAM_FILES"
orders_sequence_file=test_name+".in"
IOToolKit.validateInputFiles(working_directory+'/'+trade_flow_location,test_file=orders_sequence_file)

output_names=test_name+".out"
output_stdout="OrderBook/io/OUTPUT_FILES"


orders_gate_map=IOToolKit.parseInputFile(os.path.join(working_directory,trade_flow_location,orders_sequence_file))

f=open(os.path.join(working_directory,output_stdout,output_names),"w")
sys.stdout=f
OrderBook(incoming_orders=orders_gate_map)
f.close()



    

