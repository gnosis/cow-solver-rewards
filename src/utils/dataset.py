from dataclasses import dataclass, fields
from typing import Any


def index_by(data_list: list[dataclass], field_str: str) -> dict[Any, dataclass]:
    """
    :param data_list: list of Account structures (i.e. those having account field).
    :param field_str: field of data class to index by
    :return: mapping of Account structures by account
    """
    if len(data_list) == 0:
        return {}

    field_names = {field.name for field in fields(data_list[0])}
    assert field_str in field_names, \
        f"index field {field_str} does not exist on {type(data_list[0])}"

    results = {}
    for entry in data_list:
        index_key = entry.__dict__.get(field_str)
        if index_key not in results:
            results[index_key] = entry
        else:
            raise IndexError(f"Attempting to index by non-unique entry \"{entry}\"")
    return results