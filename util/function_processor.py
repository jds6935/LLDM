from util.tools import roll_dice, search_rules

def process_function_calls(function_name: str, **kwargs) -> any:
    """Process function calls from the LLM"""
    function_map = {
        'roll_dice': roll_dice,         # RNG tool for dice rolls
        'search_rules': search_rules,   # RAG tool for rules lookup
        'get_context': search_rules     # Alternative name for RAG lookup
    }
    
    # Log the function call (could store in game_log for history)
    print(f"Agent called function: {function_name} with args: {kwargs}")
    
    if function_name in function_map:
        result = function_map[function_name](**kwargs)
        # Log the result for debugging
        print(f"Function result: {result}")
        return result
    else:
        raise ValueError(f"Unknown function: {function_name}")