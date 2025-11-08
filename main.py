import os
from rag import RAG

API_KEY = os.environ.get("GROQ_API_KEY")


def main():
        print("=" * 60)
        print("RAG System with 1024-dim embeddings and HNSW index")
        print("=" * 60)
        
        # Initialize RAG system
        rag = RAG(api_key=API_KEY)
        
        # Display system stats
        stats = rag.get_stats()
        print("\n📊 System Statistics:")
        for key, value in stats.items():
                print(f"  • {key}: {value}")
        
        # Test queries
        queries = [
                "What is Python?",
                "Tell me about machine learning",
                "How does RAG work?"
        ]
        
        print("\n" + "=" * 60)
        print("Testing RAG Queries")
        print("=" * 60)
        
        for query in queries:
                print(f"\n❓ Query: {query}")
                response = rag.query(query, top_k=2)
                print(f"💬 Response: {response}")
                print("-" * 60)

if __name__ == "__main__":
        main()