#!/usr/bin/env python3
"""
Configurable RAG (Retrieval-Augmented Generation) Library
Using ChromaDB for vector storage, chunking, and Ollama for both embeddings and LLM generation.
"""

import os
import glob
from typing import List, Dict, Any, Optional

import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
import ollama
import json
import hashlib

class OllamaEmbeddingFunction:
    """Custom embedding function that uses Ollama for embeddings"""
    
    def __init__(self, model_name="nomic-embed-text"):
        self.model_name = model_name
    
    def __call__(self, input: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts using Ollama"""
        embeddings = ollama.embed(
            model=self.model_name,
            input=input
        )
        return embeddings.embeddings

class RAG:
    """Configuration class for the RAG library."""
    
    def __init__(
        self,
        data_dir: str = "data",
        file_extension: str = "txt",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        embedding_model: str = "nomic-embed-text",
        llm_model: str = "llama3.2:latest",
        instruction: str = "You are a helpful assistant.",
        collection_name: str = "default_collection",
        persistent: bool = False,
        db_path: Optional[str] = None,
        context_limit: int = 200,
        n_results: int = 3
    ):
        self.data_dir = data_dir
        self.file_extension = file_extension
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.instruction = instruction
        self.collection_name = collection_name
        self.persistent = persistent
        self.db_path = db_path
        self.context_limit = context_limit
        self.n_results = n_results
        self.metadata_file = os.path.join(self.db_path or ".", "db_metadata.json")
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=db_path) if persistent else chromadb.EphemeralClient()
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=OllamaEmbeddingFunction(model_name=self.embedding_model)
        )

    def compute_hash(self, data: Any) -> str:
        """Compute a hash for the given data."""
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    def load_previous_metadata(self) -> dict:
        """Load previous metadata from file if it exists."""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, "r") as f:
                return json.load(f)
        return {}

    def save_metadata(self, metadata: dict):
        """Save metadata to a file."""
        with open(self.metadata_file, "w") as f:
            json.dump(metadata, f, indent=4)

    def has_changes(self, new_metadata: dict) -> bool:
        """Check if the new metadata differs from the stored one."""
        old_metadata = self.load_previous_metadata()
        return old_metadata.get("hash") != new_metadata.get("hash")

    def start(self):
        """Initialize the RAG system only if documents or config have changed."""
        documents = self.load_documents()
        chunks = self.chunk_documents(documents)

        # Compute new metadata hash
        metadata = {
            "config": {
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap,
                "embedding_model": self.embedding_model,
                "llm_model": self.llm_model,
                "instruction": self.instruction,
                "collection_name": self.collection_name,
                "context_limit": self.context_limit,
                "n_results": self.n_results,
            },
            "documents": documents,
        }
        metadata_hash = self.compute_hash(metadata)

        if self.has_changes({"hash": metadata_hash}):
            print("Changes detected! Updating embeddings...")
            self.setup_chroma_db(chunks)
            self.save_metadata({"hash": metadata_hash})
        else:
            print("No changes detected. Using existing embeddings.")

    def load_documents(self) -> Dict[str, str]:
        """Load documents from the specified directory."""
        documents = {}
        for file_path in glob.glob(os.path.join(self.data_dir, f"*.{self.file_extension}")):
            with open(file_path, "r") as file:
                documents[os.path.basename(file_path)] = file.read()
        return documents

    def chunk_documents(self, documents: Dict[str, str]) -> List[Dict[str, Any]]:
        """Chunk documents into smaller pieces."""
        chunker = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len
        )
        chunks = []
        for doc_name, content in documents.items():
            for i, chunk in enumerate(chunker.split_text(content)):
                chunks.append({
                    "id": f"{doc_name}_chunk_{i}",
                    "text": chunk,
                    "metadata": {"source": doc_name, "chunk": i}
                })
        return chunks

    def setup_chroma_db(self, chunks: List[Dict[str, Any]]):
        """Set up ChromaDB for vector storage."""
        self.collection.add(
            ids=[chunk["id"] for chunk in chunks],
            documents=[chunk["text"] for chunk in chunks],
            metadatas=[chunk["metadata"] for chunk in chunks]
        )

    def retrieve_context(self, query: str) -> List[str]:
        """Retrieve context from the ChromaDB collection."""
        query_embedding = ollama.embed(model=self.embedding_model, input=[query]).embeddings[0]
        results = self.collection.query(query_embeddings=[query_embedding], n_results=self.n_results)
        
        return [
            f"{metadata['source']} - Chunk {metadata['chunk']}: {text}"
            for metadata_list, text_list in zip(results["metadatas"], results["documents"])
            for metadata, text in zip(metadata_list, text_list)
        ]

    def generate_response(self, query: str, contexts: List[str]) -> str:
        """Generate a response using the LLM model."""
        context_text = "\n\n".join(contexts)
        prompt = f"""{self.instruction}\n\nContext:\n{context_text}\n\nQuestion: {query}\n\nAnswer:"""
        response = ollama.generate(model=self.llm_model, prompt=prompt)
        return response["response"]

    def run_query(self, query: str) -> str:
        """Run a query on the RAG system."""
        contexts = self.retrieve_context(query)
        response = self.generate_response(query, contexts)
        #self.display_results(query, contexts, response)
        return response

    def display_results(self, query: str, contexts: List[str], response: str):
        """Display the results of the query."""
        print(f"\nQUERY: {query}\n")
        print("CONTEXT:")
        for i, context in enumerate(contexts, 1):
            print(f"Context {i}: {context[:200]}...")
        print("\nRESPONSE:")
        print(response)
