from util.llm_utils import tool_tracker
import random

@tool_tracker
def roll_dice(sides: int, number: int = 1) -> list:
    """Roll dice with specified number of sides
    Args:
        sides (int): Number of sides on the dice
        number (int): Number of dice to roll
    Returns:
        list: Results of each dice roll
    """
    return [random.randint(1, sides) for _ in range(number)]

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