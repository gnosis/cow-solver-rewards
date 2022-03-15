from dataclasses import dataclass, fields
from typing import Any


def index_by(data_list: list[dataclass], field_str: str) -> dict[Any, dataclass]:
    """
    :param data_list: list of Account structures (i.e. those having account field).
    :param field_str: field of data class to index by
    :return: mapping of Account structures by account
    """
    assert field_str in fields(data_list[0]), "index field does not exist on dataset"

    results = {}
    for entry in data_list:
        if entry['field'] not in results:
            results[entry['field']] = entry
        else:
            raise IndexError(f"Attempting to index by non-unique entry \"{entry}\"")
    return results
