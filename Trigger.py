from typing import List, Dict, Any

def filter_prompt(prompt: str) -> List[Dict[str, Any]]:
    """
    Returns a list of callable functions based on the user's prompt.
    Currently, only memory management is supported.

    Memory Function Details:
    - Always available.
    - Supports 'add' and 'delete' modes.
    - 'Update' can be implemented as a 'delete' followed by 'add'.
    - Latest information should overwrite old info if relevant.
    """
    functions: List[Dict[str, Any]] = []

    memory_function: Dict[str, Any] = {
        "function": "memory",
        "description": (
            "Manage user-specific memories. "
            "Use 'add' to store new memory, 'delete' to remove memory. "
            "For updating, first delete old info and then add the new one."
        ),
        "params": {
            "user" : "username",
            "mode": "add/delete",  # Required: 'add' or 'delete'
            "specific_memory_line": "..."  # The memory content to add or delete
        }
    }

    functions.append(memory_function)

    return functions
