def dict_has_valid_items(d, keys):
    """ Tests if the items exist and are different from None """
    return all(map(lambda key: d.get(key) is not None, keys))


def dict_contains(d, other):
    for k, v in other.items():
        if d.get(k) != v:
            return False
    return True


def is_empty(obj):
    return not bool(obj)
