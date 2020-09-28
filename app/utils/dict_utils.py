def get_sorted_list_from_dict(unsorted_dict, reverse=False):
    return [
        k
        for k, v in sorted(
            unsorted_dict.items(),
            key=lambda item: item[1], reverse=reverse
        )
    ]
