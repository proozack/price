def get_sorted_list_from_dict(unsorted_dict, reverse=False):
    return [
        k
        for k, v in sorted(
            unsorted_dict.items(),
            key=lambda item: item[1], reverse=reverse
        )
    ]
    
def sa_obj_to_dict(sa_object):
    result = {}
    for field in sa_object._fields:
        result[field] = getattr(sa_object, field, None)
    return result
