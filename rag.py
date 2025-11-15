'''
RAG sa:

IndexFlatL2 indexom
Vektorima malih dimenzija 384
Chunkovima od 512 karaktera
Popnovinim orderovanjem/cross encodingom
'''
from chromadb.config import Settings
import chromadb
from typing import List, Optional, Dict
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder

COLLECTION_NAME = "reorder"


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
                
                # Create FAISS index
                self.index = faiss.IndexFlatL2(self.embedding_dim)
                self.index.add(embeddings)
                self.doc_id_mapping = results['ids']
                print(f"FAISS index built with {len(embeddings)} vectors")

        def retrieve(self, query: str, top_k: int = 5) -> Dict:
                # nadjemo vise kandidata
                query_emb = self.embedding_model.encode([query]).astype('float32')
                # Adjust candidate count based on index size
                candidate_count = min(len(self.doc_id_mapping), max(top_k * 3, top_k + 5))
                distances, indices = self.index.search(query_emb, candidate_count)
                
                # Remove duplicates while preserving order
                doc_ids = []
                seen = set()
                for i in indices[0]:
                        doc_id = self.doc_id_mapping[i]
                        if doc_id not in seen:
                                doc_ids.append(doc_id)
                                seen.add(doc_id)
                
                # i onda ih rerankujemo
                chroma_results = self.collection.get(ids=doc_ids, include=['documents', 'metadatas'])
                docs = chroma_results['documents']
                metadatas = chroma_results.get('metadatas', [])
                pairs = [[query, doc] for doc in docs]
                scores = self.cross_encoder.predict(pairs)
                scores_with_index = [[score, index] for index, score in enumerate(scores)]
                indexes = sorted(scores_with_index,key=lambda x: x[0], reverse=True)[:top_k]
                
                return {
                        "documents": [docs[index] for score,index in indexes],
                        "doc_ids": [doc_ids[index] for score,index in indexes],
                        "metadatas": [metadatas[index] for score,index in indexes] if metadatas else [],
                        "scores": [float(score) for score,index in indexes]
                }

        def chunk_documents(self, documents: List[str], chunk_size: int = 512) -> List[str]:
                self.add_documents(documents=documents[0].split("\n"))

            
