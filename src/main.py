from src.python_tool_kit.IOToolKit import IOToolKit
import os



input_data_location=r"/Users/krzysiekbienias/Documents/GitHub/OrderBook/io"
upload_orders=True
proces_order=False


order_map=IOToolKit.parseInputFile(os.path.join(input_data_location,"test1.in"))



print("Hello matherfacker")
