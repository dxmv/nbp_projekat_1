# from disable_warnings import disable_warning_messages
# disable_warning_messages()
import os
import time
from rag import CrossRankingRAG
from hnsw import HnswRAG
from pdf_parser import PDFParser
from groq import Groq

API_KEY = os.environ.get("GROQ_API_KEY")
MODEL = "llama-3.3-70b-versatile"

def generate_response(query: str, context: str) -> str:
        """Generate a response using Groq LLM."""
        prompt = f"""
        You are a helpful assistant that can answer questions about the following context:
        {context}
        Question: {query}
        Answer:
        """
        response = Groq(api_key=API_KEY).chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
        )
        return response.choices[0].message.content

def load_pdf_into_rags(pdf_path: str, force_reload: bool = False):
        """
        Load PDF into both RAG systems.
        
        Args:
                pdf_path: Path to the PDF file
                force_reload: If True, reload even if collections exist
        """
        print("="*80)
        print("Initializing RAG systems...")
        print("="*80)
        
        # Initialize both RAG systems
        chapter_rag = HnswRAG()  # For chapters/subchapters
        paragraph_rag = CrossRankingRAG()  # For paragraphs
        
        # Check if we need to load data
        chapter_count = chapter_rag.collection.count()
        paragraph_count = paragraph_rag.collection.count()
        
        if not force_reload and chapter_count > 0 and paragraph_count > 0:
                print(f"\nData already loaded:")
                print(f"  - Chapter RAG: {chapter_count} documents")
                print(f"  - Paragraph RAG: {paragraph_count} documents")
                print("\nSkipping data loading. Set force_reload=True to reload.")
                return chapter_rag, paragraph_rag
        
        # Parse the PDF
        print(f"\nParsing PDF: {pdf_path}")
        parser = PDFParser(pdf_path)
        
        # Extract chapters and subchapters
        print("\n" + "="*80)
        print("Extracting chapters and subchapters...")
        chapters = parser.extract_chapters_and_subchapters()
        print(f"Found {len(chapters)} chapters/subchapters")
        
        # Load into chapter RAG (HNSW)
        if len(chapters) > 0:
                print("\nLoading chapters into HNSW RAG...")
                chapter_docs = [ch['content'] for ch in chapters]
                chapter_ids = [f"ch_{i}" for i in range(len(chapters))]
                chapter_metadatas = [{
                        'chapter': ch['chapter'],
                        'chapter_number': ch['chapter_number'],
                        'subchapter': ch.get('subchapter', ''),
                        'title': ch['title'],
                        'page_start': str(ch['page_start']),
                        'page_end': str(ch['page_end'])
                } for ch in chapters]
                
                chapter_rag.add_documents(
                        documents=chapter_docs,
                        ids=chapter_ids,
                        metadatas=chapter_metadatas
                )
        
        # Extract paragraphs
        print("\n" + "="*80)
        print("Extracting paragraphs...")
        paragraphs = parser.extract_paragraphs()
        print(f"Found {len(paragraphs)} paragraphs")
        
        # Load into paragraph RAG (FlatL2 + reranking)
        if len(paragraphs) > 0:
                print("\nLoading paragraphs into FlatL2 RAG...")
                para_docs = [p['content'] for p in paragraphs]
                para_ids = [f"para_{i}" for i in range(len(paragraphs))]
                para_metadatas = [{
                        'chapter': p['chapter'],
                        'chapter_number': p['chapter_number'],
                        'subchapter': p.get('subchapter', ''),
                        'page_start': str(p['page_start']),
                        'page_end': str(p['page_end'])
                } for p in paragraphs]
                
                paragraph_rag.add_documents(
                        documents=para_docs,
                        ids=para_ids,
                        metadatas=para_metadatas
                )
        
        parser.close()
        print("\n" + "="*80)
        print("PDF loaded successfully into both RAG systems!")
        print("="*80)
        
        return chapter_rag, paragraph_rag

def format_metadata(metadata: dict) -> str:
        """Format metadata for display."""
        parts = []
        if metadata.get('chapter'):
                parts.append(f"Chapter {metadata['chapter']}")
        if metadata.get('subchapter'):
                parts.append(f"Section {metadata['subchapter']}")
        if metadata.get('title'):
                parts.append(f"'{metadata['title']}'")
        if metadata.get('page_start'):
                if metadata.get('page_end') and metadata['page_start'] != metadata['page_end']:
                        parts.append(f"Pages {metadata['page_start']}-{metadata['page_end']}")
                else:
                        parts.append(f"Page {metadata['page_start']}")
        return " | ".join(parts)

def query_both_systems(chapter_rag, paragraph_rag, query: str, top_k: int = 3):
        """
        Query both RAG systems and display results.
        """
        print("\n" + "="*80)
        print(f"QUERY: {query}")
        print("="*80)
        
        # Query Chapter RAG (HNSW)
        print("\n[1] CHAPTER-BASED RAG (HNSW + Large Embeddings)")
        print("-"*80)
        start_time = time.time()
        chapter_results = chapter_rag.retrieve(query, top_k=top_k)
        chapter_time = time.time() - start_time
        
        print(f"Retrieval time: {chapter_time:.4f} seconds")
        print(f"\nTop {top_k} results:")
        for i, (doc, metadata) in enumerate(zip(chapter_results['documents'], 
                                                 chapter_results['metadatas']), 1):
                print(f"\n  Result {i}:")
                print(f"  Metadata: {format_metadata(metadata)}")
                print(f"  Content preview: {doc[:200]}...")
        
        # Query Paragraph RAG (FlatL2 + Reranking)
        print("\n" + "="*80)
        print("[2] PARAGRAPH-BASED RAG (FlatL2 + Small Embeddings + Reranking)")
        print("-"*80)
        start_time = time.time()
        para_results = paragraph_rag.retrieve(query, top_k=top_k)
        para_time = time.time() - start_time
        
        print(f"Retrieval time: {para_time:.4f} seconds")
        print(f"\nTop {top_k} results:")
        for i, (doc, metadata, score) in enumerate(zip(para_results['documents'], 
                                                        para_results['metadatas'],
                                                        para_results['scores']), 1):
                print(f"\n  Result {i} (score: {score:.4f}):")
                print(f"  Metadata: {format_metadata(metadata)}")
                print(f"  Content preview: {doc[:200]}...")
        
        # Generate LLM response using best result from each system
        print("\n" + "="*80)
        print("GENERATED RESPONSES")
        print("="*80)
        
        if chapter_results['documents']:
                print("\n[1] Response from Chapter-based RAG:")
                print("-"*80)
                response1 = generate_response(query, chapter_results['documents'][0])
                print(response1)
        
        if para_results['documents']:
                print("\n[2] Response from Paragraph-based RAG:")
                print("-"*80)
                response2 = generate_response(query, para_results['documents'][0])
                print(response2)
        
        print("\n" + "="*80)
        print("COMPARISON")
        print("="*80)
        print(f"Chapter RAG retrieval time: {chapter_time:.4f}s")
        print(f"Paragraph RAG retrieval time: {para_time:.4f}s")
        print(f"Speed difference: {abs(chapter_time - para_time):.4f}s")

def main():
        """Main function."""
        pdf_path = "data/crafting-interpreters.pdf"
        
        # Load PDF into both RAG systems
        chapter_rag, paragraph_rag = load_pdf_into_rags(pdf_path, force_reload=False)
        
        # Example queries
        queries = [
                "What is lexical analysis and scanning?",
                "How do interpreters work?",
                "What are the different types of programming languages?"
        ]
        
        print("\n\n" + "="*80)
        print("DEMO: Querying both RAG systems")
        print("="*80)
        
        # Query the first example
        query_both_systems(chapter_rag, paragraph_rag, queries[0], top_k=3)
        
        # Interactive mode
        print("\n\n" + "="*80)
        print("INTERACTIVE MODE")
        print("="*80)
        print("Enter your questions (or 'quit' to exit):")
        
        while True:
                query = input("\nYour question: ").strip()
                if query.lower() in ['quit', 'exit', 'q']:
                        print("Goodbye!")
                        break
                if query:
                        query_both_systems(chapter_rag, paragraph_rag, query, top_k=3)

if __name__ == "__main__":
        main()
