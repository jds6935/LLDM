# The Plan

### Premise:
a DnD dungeon master LLM model

### Specifications
#### Three Goals for project:
##### Dungeon Master Speech
- Descriptions: Setting, appearance, item descriptions. How attacking was stylized
- Rolls: RNG function dice rolls for actions. RNG scenerios like attacks, defence, dialouge, loot, loot variety, etc.
- Transaction: The user should be able to interact with and transact with an ai trader.
- In the system prompt, the LLM would be given the prompt templates for each individual action.
- There will be a variable called game state which will keep track of what is currently being done in the game: Attacking, Trading, Traveling, etc..
- Each interaction will
##### Coherence system (RAG)
- Have summary agent to generate a summary of each agent and track major plot points
- Parse outpus and keep track of quantitative and qualitative data about player (inader?) to maintain coherence with LLM. Stored in json format
```json
{
    "coin count" : 12,
    "coin appearance": "a two headed dragon is imprinted on the coins face."
}
```
- json would be filled in as a "reminder"
- Relationship metrics w/ virtual party

#### Other
- Networking: Utilizing the networking feature to connect the users into a session
- Premake story before hand (generally) for heros story
- Pretraining on DnD Dataset "Critical Role" ""
