from util.base import DungeonMaster

def test_dm_responses():
    dm = DungeonMaster()
    
    # Test initial message
    initial_response = dm.dm_turn_hook()
    print(f"Initial response: {initial_response}")
    
    # Test subsequent message
    dm.start = False
    dm.game_log.append("[Player] I want to search the room")
    response = dm.dm_turn_hook()
    print(f"Follow-up response: {response}")

if __name__ == "__main__":
    test_dm_responses()