import re
from typing import Union, List
from util.llm_utils import tool_tracker
import random

def extract_number(input_value: Union[str, int, dict]) -> int:
    """Extract the first number from various input types
    Args:
        input_value: Can be string, int, or dict
    Returns:
        int: First number found or 1 as default
    """
    if isinstance(input_value, int):
        return abs(input_value)
    elif isinstance(input_value, str):
        # Find first number in string (handles "d20", "20 sided", etc)
        matches = re.findall(r'\d+', input_value)
        return int(matches[0]) if matches else 1
    elif isinstance(input_value, dict):
        # Handle dictionary inputs
        for key, value in input_value.items():
            if isinstance(value, (int, str)):
                result = extract_number(value)
                if result > 0:
                    return result
    return 1  # Default fallback

@tool_tracker
def roll_dice(sides: Union[str, int, dict], number: Union[str, int, dict] = 1) -> List[int]:
    """Roll dice with specified number of sides
    Args:
        sides: Number of sides on the dice (accepts various formats)
        number: Number of dice to roll (accepts various formats)
    Returns:
        list: Results of each dice roll
    """
    try:
        # Handle D&D style notation (e.g., {'d20': 1})
        if isinstance(sides, dict):
            for key, value in sides.items():
                if not isinstance(key, str):
                    continue
                dice_type = key.lower()
                if dice_type.startswith('d'):
                    try:
                        parsed_sides = int(dice_type[1:])  # Extract number after 'd'
                        parsed_number = int(value)  # Number of dice must be integer
                        break
                    except ValueError:
                        continue
            else:  # If no valid dice notation found
                raise ValueError(f"Invalid dice notation: {sides}")
        else:
            parsed_sides = extract_number(sides)
            parsed_number = extract_number(number)
        
        # Ensure reasonable limits
        parsed_sides = min(max(parsed_sides, 2), 100)  # Between 2 and 100 sides
        parsed_number = min(max(parsed_number, 1), 10)  # Between 1 and 10 dice
        
        return [random.randint(1, parsed_sides) for _ in range(parsed_number)]
    except Exception as e:
        print(f"[DEBUG] Dice roll failed - sides: {sides}, number: {number}")
        print(f"[ERROR] {e}")
        return [1]  # Return default roll on error

@tool_tracker
def search_rules(query: str) -> str:
    """Search D&D rules documentation
    Args:
        query (str): Search query for rules lookup
    Returns:
        str: Relevant rule text
    """
    # Implement your RAG logic here
    return f"Found rule for {query}..."