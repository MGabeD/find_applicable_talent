from typing import List
import operator
from find_applicable_talent.backend.util.logger import get_logger

logger = get_logger(__name__)

OPERATORS = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "in": lambda val, container: val in container,
    "contains": lambda container, val: val in container, 
}


def _collect_next_level(value, remaining_parts):
    if isinstance(value, list):
        # Collect matches from each item in the list
        all_results = []
        for item in value:
            all_results.extend(_extract(item, remaining_parts))
        return all_results
    else:
        # Not a list → just extract from this single value
        return _extract(value, remaining_parts)
    

def _extract(obj, parts):
    if not parts:
        # return list so callers can use `any(...)`
        return [obj]

    key, *remaining = parts

    # Lists: dive into every item with the *same* parts list
    if isinstance(obj, list):
        results = []
        for item in obj:
            results.extend(_extract(item, parts))     # unchanged parts
        return results

    # Attribute access on Pydantic model / plain object
    if hasattr(obj, key):
        return _extract(getattr(obj, key), remaining)

    # Dict support (optional – useful if you load raw JSON)
    if isinstance(obj, dict) and key in obj:
        return _extract(obj[key], remaining)

    return []


def get_values_by_path(obj, path: str):
    parts = path.split('.')
    return _extract(obj, parts)


def safe_compare(value, target_value, op):
    try:
        if isinstance(value, str):
            value = "".join(value.lower().split())
        if isinstance(target_value, str):
            target_value = "".join(target_value.lower().split())
        return op(value, target_value)
    except Exception as e:
        logger.error(f"Error comparing {value} and {target_value} with {op}: {e}")
        return False


def build_filter_functions(path: str, operator_key: str, target_value):
    if operator_key not in OPERATORS:
        raise ValueError(f"Invalid operator: {operator_key}")
    
    op = OPERATORS[operator_key]

    def filter_function(candidate):
        values = get_values_by_path(candidate, path)
        if not values:
            return False
        
        if operator_key == "contains":
            return any(safe_compare(value, target_value, op) for value in values)
        elif operator_key == "in":
            return any(safe_compare(value, target_value, op) for value in values)
        else:
            return any(safe_compare(value, target_value, op) for value in values)
    
    return filter_function



