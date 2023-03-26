import json
from typing import TypeVar, Iterable, Tuple, Dict, List
HM = TypeVar("HM", bound=Dict)
import os


class IOToolKit:
    
    @staticmethod
    def parseInputFile(file_name):
        """parseInputFile
        Description
        -----------
        This method uploads input data from source file. In this context it converts different test inputs into hash map. 

        Parameters
        ----------
        file_name : _type_
            _description_

        Returns
        -------
        _type_
            _description_
        """
        orders_map=dict()
        with open(file_name) as f:
            data=f.read()
        orders_container=data.splitlines()
        
        for order in orders_container:
            order_map=json.loads(order)
            id_order=order_map['order']['id']
            orders_map.update({id_order:order_map})
        return orders_map


    @staticmethod
    def validateInputFiles(inputs_path,test_file):
        if not os.path.isfile(os.path.join(inputs_path,test_file)):
            ValueError(f"There is no  test file {test_file}.")


