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
            llm_model="llama3.2:latest", # Language model for response generation
            instruction="Based on the input give me any information that the DM should know to make better and more accurate story telling.",  # LLM prompt style
            collection_name="my_rag_collection",  # ChromaDB collection name
            persistent=True,            # Whether to persist ChromaDB storage
            db_path="./chroma_db",      # Path for persistent storage
            context_limit=200,          # Max characters to display in context
            n_results=4                 # Number of relevant documents to retrieve
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
        print("[DEBUG] Starting DM turn...")
        try:
            # 1. Agent makes RAG tool call for additional context
            rag_context = ""
            if not self.start:
                # Extract important questions from game log to ask RAG
                last_messages = "\n".join(self.game_log[-5:])  # Get last 5 messages
                try:
                    # Ask RAG system about relevant game rules or context
                    rag_context = self.rag.run_query(f"Based on this game context, what DnD rules or information should I know: {last_messages}")
                    print(f"[DEBUG] RAG context: {rag_context}")  # Debugging log
                except Exception as e:
                    print(f"RAG error: {e}")
            
            # 2. Agent output, giving scenario to players and asking for their actions
            dm_message = ''
            
            if self.start:
                # Initial game setup
                dm_message = self.chat.start_chat()
                print(f"[DEBUG] Initial DM message: {dm_message}")  # Debugging log
                self.start = False
            else:
                # Process player actions, include RAG context
                if rag_context:  # Only add RAG message if there is context
                    rag_message = f"[RAG] {rag_context}"
                    self.game_log.append(rag_message)
                    
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
            
            print(f"[DEBUG] DM response: {dm_message}")
            return dm_message
        except Exception as e:
            print(f"[ERROR] DM turn error: {e}")
            return "I apologize, but I encountered an error. Please try again."


class Player:
    def __init__(self, name, log_callback=None):
        self.name = name
        self.client = PlayerClient(self.name, log_callback=log_callback)

    def connect(self):
        self.client.connect()

    def unjoin(self):
        self.client.unjoin()

    def take_turn(self, message):
        # Simply send the message without character sheet
        self.client.send_message(message)
