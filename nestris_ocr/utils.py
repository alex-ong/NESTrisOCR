def flatten(nested_dict):
    # ref: https://github.com/simonw/json-flatten

    flattened_dict = dict()

    def _flatten(object_, key):
        # Empty object can't be iterated, take as is
        if not object_:
            flattened_dict[key] = object_
        # These object types support iteration
        elif isinstance(object_, dict):
            for object_key in object_:
                # if key:
                _flatten(
                    object_[object_key], key + "." + object_key if key else object_key
                )
        else:
            flattened_dict[key] = object_

    _flatten(nested_dict, None)
    return flattened_dict


def unflatten(flat_dict):
    # ref: https://github.com/simonw/json-flatten

    unflattened_dict = dict()

    def _unflatten(dic, keys, value):
        for key in keys[:-1]:
            dic = dic.setdefault(key, {})

        dic[keys[-1]] = value

    list_keys = sorted(flat_dict.keys())
    for i, item in enumerate(list_keys):
        if i != len(list_keys) - 1:
            if not list_keys[i + 1].startswith(list_keys[i]):
                _unflatten(unflattened_dict, item.split("."), flat_dict[item])
            else:
                pass  # if key contained in next key, json will be invalid.
        else:
            #  last element
            _unflatten(unflattened_dict, item.split("."), flat_dict[item])
    return unflattened_dict
