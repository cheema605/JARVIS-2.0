import os
import json
import asyncio

USER_CONTEXT_FILE = "user_context.json"

# ----------------- Context Handling -----------------

def _load_user_context():
    """Load user context from JSON file; create default structure if missing."""
    if not os.path.exists(USER_CONTEXT_FILE):
        data = {"user_memories": {}, "chat_history": []}
        _save_user_context(data)
        return data
    with open(USER_CONTEXT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save_user_context(data):
    """Save context to JSON file."""
    try:
        with open(USER_CONTEXT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return {"status": "True", "message": "Context saved."}
    except Exception as e:
        return {"status": "False", "message": f"Failed to save context: {str(e)}"}

# ----------------- Memory Functions -----------------

def memory(mode: str, specific_memory_line: str = None, user: str = None):
    """
    Manage user-specific memories.
    - mode: 'add', 'delete', 'get'
    - specific_memory_line: required for add/delete
    - user: username key for memory
    """
    if not user:
        return {"status": "False", "message": "User must be provided."}

    data = _load_user_context()
    user_memories = data.setdefault("user_memories", {})
    mem_list = user_memories.setdefault(user, [])

    if mode == "add":
        if not specific_memory_line:
            return {"status": "False", "message": "No memory content provided for add."}
        if specific_memory_line not in mem_list:
            mem_list.append(specific_memory_line)
            save_status = _save_user_context(data)
            return save_status if save_status["status"] == "True" else {"status": "False", "message": save_status["message"]}
        return {"status": "False", "message": "Memory already exists."}

    elif mode == "delete":
        if not specific_memory_line:
            return {"status": "False", "message": "No memory content provided for delete."}
        if specific_memory_line in mem_list:
            mem_list.remove(specific_memory_line)
            save_status = _save_user_context(data)
            return save_status if save_status["status"] == "True" else {"status": "False", "message": save_status["message"]}
        return {"status": "False", "message": "Memory not found."}

    elif mode == "get":
        return {"status": "True", "data": mem_list}

    return {"status": "False", "message": f"Invalid mode '{mode}'. Use 'add', 'delete', or 'get'."}

# ----------------- Chat History Functions -----------------

def add_chat_history(role: str, message: str, user: str = None):
    """
    Append a chat entry.
    - role: 'user', 'jarvis', or 'system'
    - user: optional user for memory linking/logging
    """
    if not role or not message:
        return {"status": "False", "message": "Role and message must be provided."}

    data = _load_user_context()
    entry = {"role": role, "message": message}
    if user:
        entry["user"] = user

    data.setdefault("chat_history", []).append(entry)
    # Limit chat history to last 20 entries
    data["chat_history"] = data["chat_history"][-20:]

    save_status = _save_user_context(data)
    return save_status if save_status["status"] == "True" else {"status": "False", "message": save_status["message"]}

def get_chat_history(limit: int = 20):
    """Return the last `limit` chat entries."""
    data = _load_user_context()
    history = data.get("chat_history", [])
    return {"status": "True", "data": history[-limit:] if len(history) > limit else history}

# ----------------- Async Placeholders for Future Functions -----------------

async def send_email(to: str, subject: str, body: str):
    """Placeholder async email function."""
    await asyncio.sleep(0.1)
    return {"status": "False", "message": "Email function not active."}

async def turn_on_light(location: str):
    await asyncio.sleep(0.1)
    return {"status": "False", "message": "Light control not active."}

async def shutdown():
    await asyncio.sleep(0.1)
    return {"status": "False", "message": "Shutdown function not active."}

# ----------------- Unified Function Dispatcher -----------------

async def execute_function(func_name: str, params: dict):
    """
    Execute any function by name with params.
    Handles memory, chat history, and async placeholders.
    Returns standardized result.
    """
    try:
        if func_name == "memory":
            return memory(params.get("mode"), params.get("specific_memory_line"), params.get("user"))
        elif func_name == "add_chat_history":
            return add_chat_history(params.get("role"), params.get("message"), params.get("user"))
        elif func_name == "get_chat_history":
            return get_chat_history(params.get("limit", 20))
        elif func_name == "send_email":
            return await send_email(params.get("to"), params.get("subject"), params.get("body"))
        elif func_name == "turn_on_light":
            return await turn_on_light(params.get("location"))
        elif func_name == "shutdown":
            return await shutdown()
        else:
            return {"status": "False", "message": f"Function '{func_name}' not implemented."}
    except Exception as e:
        return {"status": "False", "message": f"Function '{func_name}' failed: {str(e)}"}
