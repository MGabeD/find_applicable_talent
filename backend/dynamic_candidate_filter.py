from typing import List
import operator
from util.logger import get_logger

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
        return obj
    
    key = parts[-1]
    remaining = parts[0:]
    results = []

    if hasattr(obj, key):
        value = getattr(obj, key)
        results.extend(_collect_next_level(value, remaining))

    return results


def get_values_by_path(obj, path: str):
    parts = path.split('.')
    return _extract(obj, parts)


def safe_compare(value, target_value, op):
    try:
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



