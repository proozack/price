from . import dict_utils
from . import list_utils

import logging
log = logging.getLogger(__name__)

skip_characters = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '-', '+', '+', '|', '\\', '{', '[', ']', '}', ':', ';', '"', '\'', '<', ',', '>', '.', '?', '/', '`', '~']

akcept_characters = ['/', ' ', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+', '+', '|', '\\', '{', '[', ']', '}', ':', ';', '"', '\'', '<', ',', '>', '.', '?', '/', '`', '~']

class StringUtils():
    
    def calculate_characters(self, string: str) -> dict:
        calculate = {}
        for char in string:
            # if char in skip_characters:
            if char in akcept_characters:
                if calculate.get(char, None) is None:
                    calculate[char] = 1
                else:
                    calculate[char] = calculate.get(char, None) + 1
        return dict_utils.get_sorted_list_from_dict(calculate, True)

    def split_string(self, string: str) -> list:
        delimiter_list = self.calculate_characters(string)
        if len(delimiter_list)==0:
            return []
        return string.split(delimiter_list[0])

    def multisplit_string(self, string: str, **kwargs) -> list:
        """
        method return list string spliting by multiple delimiter
        :param string
        :return list
        """
        lower = kwargs.get('lower')
        delimiter_list = self.calculate_characters(string)
        if len(delimiter_list)==0:
            return [
                string.lower() if lower else string
            ]
        global_list = [string,]
        global_list = list_utils.reduce_list(global_list)
        for delimiter in delimiter_list:
            temp_list = []
            for key in global_list:
                if not isinstance(key, list):
                    result = key.split(delimiter)
                    temp_list.append(result)
            global_list = list_utils.reduce_list(temp_list)
                
        return [
            key.lower() if lower else key
            for key in global_list if len(key)>0
        ]
