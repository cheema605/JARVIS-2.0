import asyncio
from workflow_calls import execute_function

async def call_corresponding_func(functions: list):
    """
    Accepts a list of functions (with params) and executes them locally.
    Handles both synchronous and async functions.
    Returns a dict with each function's result.
    """
    if not functions:
        return {"status": "False", "message": "No functions to execute."}

    results = {}

    for func in functions:
        func_name = func.get("function", "unknown_function")
        params = func.get("params", {})
        print(f"🛠 Executing: {func_name} with params: {params}")

        try:
            # execute_function handles async internally if needed
            func_result = await execute_function(func_name, params)
            results[func_name] = {
                "function": func_name,
                "status": func_result.get("status", "False"),
                "response": func_result
            }
        except Exception as e:
            results[func_name] = {
                "function": func_name,
                "status": "False",
                "error": str(e)
            }

    return results
