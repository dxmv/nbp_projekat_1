'''
RAG sa:

HNSW indexom
Vektorima velikih dimenzija
Sementicnim chunkingom 
Binarnom kvantizacijom
'''

from chromadb.config import Settings
import chromadb
from typing import List, Optional, Dict
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder

COLLECTION_NAME = "hnsw"


class HnswRAG:
        def __init__(self, 
                     embedding_model: str = "BAAI/bge-large-en-v1.5"):
                self.embedding_model = SentenceTransformer(embedding_model)
                self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
                self.index = None

                # Inicijalizacija ChromaDB with persistence
                self.chroma = chromadb.PersistentClient(path="./rag")
                self.collection = self.chroma.get_or_create_collection(COLLECTION_NAME)

        def add_documents(self, documents: List[str], ids: Optional[List[str]] = None, 
                         metadatas: Optional[List[Dict]] = None):
                # Generisanje ID-jeva ako nisu dostavljeni
                if ids is None:
                        ids = [str(i) for i in range(len(documents))]
                
                # ChromaDB batch size limit
                batch_size = 5000
                total_docs = len(documents)
                
                # Process in batches
                for i in range(0, total_docs, batch_size):
                        end_idx = min(i + batch_size, total_docs)
                        batch_docs = documents[i:end_idx]
                        batch_ids = ids[i:end_idx]
                        batch_metadatas = metadatas[i:end_idx] if metadatas else None
                        
                        # Generisanje embeddinga za batch
                        embeddings = self.embedding_model.encode(batch_docs).tolist()
                        
                        # Dodavanje u ChromaDB sa metadatama
                        if batch_metadatas:
                                self.collection.add(documents=batch_docs, embeddings=embeddings, 
                                                  ids=batch_ids, metadatas=batch_metadatas)
                        else:
                                self.collection.add(documents=batch_docs, embeddings=embeddings, ids=batch_ids)
                        
                        print(f"Added batch {i//batch_size + 1}: {len(batch_docs)} documents ({i+1}-{end_idx} of {total_docs})")
                
                print(f"Total: Added {len(documents)} documents to ChromaDB")
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
                
                # Create FAISS index (dimension, M=32 neighbors)
                self.index = faiss.IndexHNSWFlat(self.embedding_dim, 32)
                self.index.add(embeddings)
                self.doc_id_mapping = results['ids']
                print(f"FAISS index built with {len(embeddings)} vectors")

        def retrieve(self, query: str, top_k: int = 5) -> Dict:
                # nadjemo vise kandidata
                query_emb = self.embedding_model.encode([query]).astype('float32')
                distances, indices = self.index.search(query_emb, top_k)
                # i onda ih rerankujemo
                doc_ids = [self.doc_id_mapping[i] for i in indices[0]]
                chroma_results = self.collection.get(ids=doc_ids, include=['documents', 'metadatas'])
                
                return {
                        "documents": chroma_results['documents'],
                        "doc_ids": doc_ids,
                        "metadatas": chroma_results.get('metadatas', []),
                        "distances": distances[0].tolist()
                }

        def chunk_documents(self, documents: List[str], chunk_size: int = 512) -> List[str]:
                self.add_documents(documents=documents[0].split("\n"))

            
