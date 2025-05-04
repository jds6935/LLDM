from util.dndnetwork import DungeonMasterServer, PlayerClient
from util.llm_utils import TemplateChat
from util.function_processor import process_function_calls
from rag_library import RAG


class DungeonMaster:
    def __init__(self):
        self.game_log = ['START']
        self.server = DungeonMasterServer(self.game_log, self.dm_turn_hook)
        
        # Initialize RAG system
        self.rag = RAG(
            data_dir="rag-documents",  # Directory containing text files
            file_extension="txt",      # File type to process
            chunk_size=750,            # Number of characters per chunk
            chunk_overlap=250,          # Overlapping characters between chunks
            embedding_model="nomic-embed-text",  # Embedding model for vector storage
            #llm_model="llama3.2:latest", # Language model for response generation
            instruction="You are an assistant that gives me very straight forward answers on DnD",  # LLM prompt style
            collection_name="my_rag_collection",  # ChromaDB collection name
            persistent=True,            # Whether to persist ChromaDB storage
            db_path="./chroma_db",      # Path for persistent storage
            context_limit=300,          # Max characters to display in context
            n_results=12                # Number of relevant documents to retrieve
        )
        self.rag.start()

        # Update search_rules function to use RAG
        def get_context(query: str) -> str:
            return self.rag.get_context(query)

        self.chat = TemplateChat.from_file(
            'util/templates/dm_chat.json',
            sign='hello',
            function_call_processor=process_function_calls
        )
        self.start = True
        self.summary = []  # Store summaries of game events
        self.player_stats = {}  # Store player character sheets
        self.dm_secret_knowledge = ""  # Store RAG context as DM's secret knowledge

    def start_server(self):
        self.server.start_server()

    def dm_turn_hook(self):
        # 1. Agent makes RAG tool call for additional context
        if not self.start:
            # Extract important questions from game log to ask RAG
            last_messages = "\n".join(self.game_log[-5:])  # Get last 5 messages
            try:
                # Ask RAG system about relevant game rules or context
                self.dm_secret_knowledge = self.rag.get_context(
                    f"Based on this game context, what DnD rules or information should I know: {last_messages}"
                )
                print(f"[DEBUG] RAG context (DM secret knowledge): {self.dm_secret_knowledge}")  # Debugging log
            except Exception as e:
                print(f"RAG error: {e}")
                self.dm_secret_knowledge = ""  # Clear secret knowledge on error
        
        # 2. Agent output, giving scenario to players and asking for their actions
        dm_message = ''
        
        if self.start:
            # Initial game setup
            dm_message = self.chat.start_chat()
            print(f"[DEBUG] Initial DM message: {dm_message}")  # Debugging log
            self.start = False
        else:
            # Process player actions, exclude RAG context from game log
            game_context = '\n'.join(self.game_log)
            print(f"[DEBUG] Game context: {game_context}")  # Debugging log
            dm_message = self.chat.send(game_context)
            print(f"[DEBUG] DM message after processing: {dm_message}")  # Debugging log
            
            # 5. Summarize what happened to keep context short
            if len(self.game_log) > 20:  # After 20 messages, start summarizing
                # Create a summary of recent events (excluding RAG calls)
                recent_events = "\n".join(self.game_log[-10:])  # Last 10 interactions
                summary = f"Game summary at turn {len(self.game_log)}: {recent_events[:100]}..."
                self.summary.append(summary)
                # Trim the game log to keep context manageable
                self.game_log = self.game_log[:5] + ["...SUMMARY..."] + self.summary[-1:] + self.game_log[-5:]
        
        # Add DM message to the game log only
        message_to_send = f"[DM] {dm_message}"
        self.game_log.append(message_to_send)
        
        # Just return the message, let the server handle broadcasting
        return dm_message 


class Player:
    def __init__(self, name, log_callback=None):
        self.name = name
        self.client = PlayerClient(self.name, log_callback=log_callback)
        self.character_sheet = {
            "name": name,
            "race": "Half-Elf",
            "class": "Ranger",
            "level": 3,
            "background": "Outlander",
            "alignment": "Chaotic Good",
            "abilities": {
                "strength": 12,
                "dexterity": 16, 
                "constitution": 14,
                "intelligence": 10,
                "wisdom": 14,
                "charisma": 14
            },
            "skills": {
                "nature": True,
                "survival": True,
                "stealth": True,
                "perception": True
            },
            "hp": {
                "max": 27,
                "current": 27
            },
            "armor_class": 15,
            "equipment": [
                "Leather Armor",
                "Longbow",
                "Two Shortswords",
                "Explorer's Pack"
            ]
        }  # Example character sheet

    def connect(self):
        self.client.connect()

    def unjoin(self):
        self.client.unjoin()

    def take_turn(self, message):
        # 3. Players give actions, attaching player card to message
        message_with_character = f"{message}\n\nCHARACTER: {self.character_sheet}"
        self.client.send_message(message_with_character)
