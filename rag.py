from chromadb.config import Settings
import chromadb
from typing import List, Optional, Dict
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder

COLLECTION_NAME = "rag"


class CrossRankingRAG:
        def __init__(self, 
                     embedding_model: str = "all-MiniLM-L6-v2",
                     cross_encoder_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
                self.embedding_model = SentenceTransformer(embedding_model)
                self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
                self.cross_encoder = CrossEncoder(cross_encoder_model)
                self.index = None

                # Inicijalizacija ChromaDB with persistence
                self.chroma = chromadb.PersistentClient(path="./rag")
                self.collection = self.chroma.get_or_create_collection(COLLECTION_NAME)

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
                self.index = faiss.IndexFlatL2(self.embedding_dim)
                self.index.add(embeddings)
                self.doc_id_mapping = results['ids']
                print(f"FAISS index built with {len(embeddings)} vectors")

        def retrieve(self, query: str, top_k: int = 5) -> Dict:
                # nadjemo vise kandidata
                query_emb = self.embedding_model.encode([query]).astype('float32')
                distances, indices = self.index.search(query_emb, top_k*3)
                # i onda ih rerankujemo
                doc_ids = [self.doc_id_mapping[i] for i in indices[0]]
                chroma_results = self.collection.get(ids=doc_ids, include=['documents'])
                docs = chroma_results['documents']
                pairs = [[query, doc] for doc in docs]
                scores = self.cross_encoder.predict(pairs)
                scores_with_index = [[score, index] for index, score in enumerate(scores)]
                indexes = sorted(scores_with_index,key=lambda x: x[0], reverse=True)[:top_k]
                
                return {
                        "documents": [docs[index] for score,index in indexes],
                        "doc_ids": [doc_ids[index] for score,index in indexes],
                        "scores": [float(score) for score,index in indexes]
                }

        def chunk_documents(self, documents: List[str], chunk_size: int = 512) -> List[str]:
                self.add_documents(documents=documents[0].split("\n"))

            
