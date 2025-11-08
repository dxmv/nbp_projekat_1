from groq import Groq
from chromadb.config import Settings
import chromadb
from typing import List, Optional
from sentence_transformers import SentenceTransformer


SOURCE_FILE = "data/test.txt"
COLLECTION_NAME = "rag"
DOCUMENTS = [
    "Python is a high-level programming language known for its simplicity and readability.",
    "Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
    "Natural Language Processing (NLP) helps computers understand and process human language.",
    "Deep learning uses neural networks with multiple layers to process complex patterns.",
    "RAG systems combine retrieval mechanisms with generative AI to provide accurate answers."
]

class RAG:
        def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile", embedding_model: str = "BAAI/bge-large-en-v1.5"):
                self.api_key = api_key
                self.model = model
                self.llm_client = Groq(api_key=api_key)
                # BAAI/bge-large-en-v1.5 produces 1024-dimensional embeddings
                self.embedding_model = SentenceTransformer(embedding_model)
                print(f"Using embedding model: {embedding_model} (1024 dimensions)")

                # Initialize ChromaDB with persistence and HNSW index
                self.chroma_client = chromadb.PersistentClient(
                    path="./rag",
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )
                # Get or create collection with HNSW index (default in ChromaDB)
                try:
                        self.collection = self.chroma_client.get_collection(COLLECTION_NAME)
                        print(f"Loaded existing collection: {COLLECTION_NAME} with HNSW index")
                except:
                        self.collection = self.chroma_client.create_collection(
                                name=COLLECTION_NAME,
                                metadata={"description": "RAG document store"}
                        )
                        print(f"Created new collection: {COLLECTION_NAME} with HNSW index")

                self.add_documents(documents=DOCUMENTS)

        def add_documents(self, documents: List[str], ids: Optional[List[str]] = None):
                # Generisanje ID-jeva ako nisu dostavljeni
                if ids is None:
                        ids = [str(i) for i in range(len(documents))]
                
                # Generisanje embeddinga
                embeddings = self.embedding_model.encode(documents).tolist()
                
                # Dodavanje u ChromaDB
                self.collection.add(documents=documents, embeddings=embeddings, ids=ids)
                
                print(f"Added {len(documents)} documents to ChromaDB")
                self._build_index()

        def _build_index(self):
                # Get all documents from ChromaDB
                results = self.collection.get(include=['embeddings', 'documents'])
        
                # Provera da li ima embeddinga
                if results['embeddings'] is None or len(results['embeddings']) == 0:
                        print("No embeddings in ChromaDB yet. FAISS index will be built after adding documents.")
                        return
        

            
