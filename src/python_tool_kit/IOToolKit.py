import json


class IOToolKit:

    def parseInputFile(file_name):
        orders_map=dict()
        with open(file_name) as f:
            data=f.read()
        orders_container=data.splitlines()
        
        for order in orders_container:
            order_map=json.loads(order)
            id_order=order_map['order']
           

            
        return orders_map

