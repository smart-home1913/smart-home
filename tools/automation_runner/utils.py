import operator

from db.automation import Operator


def _string_to_bool(string: str):
    if string.lower() == "true":
        return True
    elif string.lower() == "false":
        return False
    else:
        raise ValueError("Non bool value returned")


def _string_to_float(string: str):
    try:
        return float(string)
    except ValueError:
        print(f"Error: '{string}' cannot be converted to a float.")
        return None


def _apply_comparison(op: Operator, a: float, b: float) -> bool:
    comparison_func = _enum_to_operator(op)
    return comparison_func(a, b)


def _enum_to_operator(op: Operator):
    operator_map = {
        Operator.GREATER: operator.gt,
        Operator.LESS: operator.lt,
        Operator.LESS_EQUAL: operator.le,
        Operator.GREATER_EQUAL: operator.ge,
        Operator.EQUAL: operator.eq,
        Operator.NOT_EQUAL: operator.ne
    }

    if op not in operator_map:
        raise ValueError(f"Unsupported operator: {op}")

    return operator_map[op]