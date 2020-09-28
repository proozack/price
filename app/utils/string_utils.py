from . import dict_utils
from . import list_utils

skip_characters = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '-', '+', '+', '|', '\\', '{', '[', ']', '}', ':', ';', '"', '\'', '<', ',', '>', '.', '?', '/', '`', '~']

class StringUtils():
    
    def calculate_characters(self, string: str) -> dict:
        calculate = {}
        for char in string:
            if char in skip_characters:
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

    def multisplit_string(self, string: str) -> list:
        """
        method return list string spliting by multiple delimiter
        :param string
        :return list
        """
        delimiter_list = self.calculate_characters(string)
        if len(delimiter_list)==0:
            return []
        global_list = [string,]
        global_list = list_utils.reduce_list(global_list)
        for delimiter in delimiter_list:
            for key in global_list:
                if not isinstance(key, list):
                    result = key.split(delimiter)
                    global_list.remove(key)
                    global_list.append(result)
                    global_list = list_utils.reduce_list(global_list)
        
        return [
            key
            for key in global_list if len(key)>0
        ]
