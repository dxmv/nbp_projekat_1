from chromadb.config import Settings
import chromadb
from typing import List, Optional, Dict
import faiss
import numpy as np
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
        def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
                self.embedding_model = SentenceTransformer(embedding_model)
                self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
                self.index = None

                # Inicijalizacija ChromaDB with persistence
                self.chroma = chromadb.PersistentClient(path="./rag")
                self.collection = self.chroma.get_or_create_collection(COLLECTION_NAME)

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
                # Convert to numpy array
                embeddings = np.array(results['embeddings']).astype('float32')
                
                # Create FAISS index
                self.index = faiss.IndexFlatIP(self.embedding_dim)
                self.index.add(embeddings)
                self.doc_id_mapping = results['ids']
                print(f"FAISS index built with {len(embeddings)} vectors")

        def retrieve(self, query: str, top_k: int = 3) -> Dict:
                query_emb = self.embedding_model.encode([query]).astype('float32')
                distances, indices = self.index.search(query_emb, top_k)
                doc_ids = [self.doc_id_mapping[i] for i in indices[0]]
                chroma_results = self.collection.get(ids=doc_ids, include=['documents'])
                return {
                        "documents": chroma_results['documents'],
                        "distances": distances[0].tolist(),
                        "doc_ids": doc_ids,
                }
        

            
