
def reduce_list(list_to_reduce):
    lista = []
    for item in list_to_reduce:
        if isinstance(item, list):
            lista.extend(reduce_list(item))
        else:
            lista.append(item)
    return lista

def remove_duplicates(list_to_clear):
    return list(dict.fromkeys(list_to_clear))
