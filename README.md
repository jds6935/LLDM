# LLDM

## Setup:
- Players make character sheets
- Agent generates overarching plot

## Game Loop
1. Agent makes RAG tool call asking questions and getting additional context
2. Agent output, giving scenerio to players and asking for players actions
3. players give actions, attaching player card to message
4. Agent runs RNG tool, to get dice rolls if need.
5. Agent summarizes what happened up to this point to keep short context, excludes RAG context calls from context.
6. return to step 1.

### tools
1. RNG
2. RAG

### Extras
1. Text to speech
2. Speech to text

### Requirements

## Configuration and Launch

### Server Setup
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure server settings in `config.json`:
```json
{
    "host": "127.0.0.1",
    "port": 5555,
    "max_players": 4
}
```

### Starting the Game
1. Launch the Dungeon Master server:
```bash
python3 game.py
```

2. Launch player clients:
```bash
python3 player.py
```

3. In the player client:
   - Click "Connect" to join the game
   - Toggle Text-to-Speech if desired
   - Use the text input to send messages
   - Use the Record button for voice input

### Notes
- The server must be running before players can connect
- Each player needs their own instance of the client
- All players must be connected before the game begins
- Character sheets should be prepared before connecting
