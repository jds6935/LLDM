# Set up RAG configuration
from rag_library import RAG
import tkinter
from util.dndnetwork import DungeonMasterServer

rag = RAG(
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

rag.start()

# Initialize game log
game_log = []

def main():
    
    # Create a Tkinter window
    root = tkinter.Tk()
    root.title("DnD Assistant")
    
    # Add a text widget to display the game log
    log_label = tkinter.Label(root, text="Game Log:")
    log_label.pack()
    log_text = tkinter.Text(root, height=10, width=50)
    log_text.pack()
    
    # Function to update the log display
    def update_log_display():
        log_text.delete(1.0, tkinter.END)
        log_text.insert(tkinter.END, ''.join(game_log))
        root.after(1000, update_log_display)  # Update every second
    
    # Start the log updates
    update_log_display()
    
    # Create a text box for the query input
    query_label = tkinter.Label(root, text="Enter your query:")
    query_label.pack()
    query_entry = tkinter.Entry(root, width=50)
    query_entry.pack()

    # Create a text box for displaying the response
    response_label = tkinter.Label(root, text="Response:")
    response_label.pack()
    response_text = tkinter.Text(root, height=10, width=50)
    response_text.pack()

    # Function to handle the query submission
    def submit_query():
        query = query_entry.get()
        response = rag.get_context(query)
        response_text.delete(1.0, tkinter.END)
        response_text.insert(tkinter.END, response)

    # Create a submit button
    submit_button = tkinter.Button(root, text="Submit", command=submit_query)
    submit_button.pack()

    # Run the Tkinter event loop
    root.mainloop()


if __name__ == "__main__": 
    main()