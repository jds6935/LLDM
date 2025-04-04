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
