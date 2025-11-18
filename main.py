import os
import time
from rag import CrossRankingRAG
from hnsw import HnswRAG
from pdf_parser import PDFParser
from groq import Groq

API_KEY = os.environ.get("GROQ_API_KEY")
MODEL = "llama-3.3-70b-versatile"
PDF_PATH = "data/crafting-interpreters.pdf"
DIVIDE = 80
QUESTIONS = [
        # "Explain the difference between statements and expressions in Lox",\
        # "List all types of expressions and statements in Lox",
        "What does the Resolver class do in Lox?"
]

def generate_response(query: str, context: str) -> str:
        prompt = f"""
        You are a helpful assistant that can answer questions about the following context:
        {context}
        Question: {query}
        """
        response = Groq(api_key=API_KEY).chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2048
        )
        return response.choices[0].message.content

def load_pdf_into_rags():
        print("="*DIVIDE)

        hnsw_rag = HnswRAG()  
        crossranking_rag = CrossRankingRAG()  
        
        hnsw_count = hnsw_rag.collection.count()
        crossranking_count = crossranking_rag.collection.count()
        # da li trebamo opet da dodamo pdf 
        if hnsw_count > 0 and crossranking_count > 0:
                print("PDF already loaded into RAG")
                return crossranking_rag, hnsw_rag
        
        
        print(f"\nParsing PDF: {PDF_PATH}")
        parser = PDFParser(PDF_PATH)
        
        print("Extracting paragraphs...")
        paragraphs = parser.extract_paragraphs()
        print(f"Found {len(paragraphs)} paragraphs")
        print("Extracting large chunks...")
        large_chunks = parser.extract_large_chunks()
        print(f"Found {len(large_chunks)} large chunks")
        
        # dodajemo paragrafe u crossranking rag
        if len(paragraphs) > 0:
                print("Loading paragraphs into FlatL2 RAG...")
                para_docs = [p['content'] for p in paragraphs]
                para_ids = [f"para_{i}" for i in range(len(paragraphs))]
                # metadata
                para_metadatas = [{
                        'chapter': p['chapter'],
                        'chapter_number': p['chapter_number'],
                        'subchapter': p.get('subchapter', ''),
                        'page_start': str(p['page_start']),
                        'page_end': str(p['page_end'])
                } for p in paragraphs]
                crossranking_rag.add_documents(
                        documents=para_docs,
                        ids=para_ids,
                        metadatas=para_metadatas
                )
                print(f"FlatL2 RAG built successfully with {len(paragraphs)} paragraphs")
        
        # chunkovi u hnsw rag
        if len(large_chunks) > 0:
                print("Loading chunks into HNSW RAG...")
                chunk_docs = [c['content'] for c in large_chunks]
                chunk_ids = [f"chunk_{i}" for i in range(len(large_chunks))]
                chunk_metadatas = [{
                        'chapter': c['chapter'],
                        'chapter_number': c['chapter_number'],
                        'subchapter': c.get('subchapter', ''),
                        'page_start': str(c['page_start']),
                        'page_end': str(c['page_end'])
                } for c in large_chunks]
                hnsw_rag.add_documents(
                        documents=chunk_docs,
                        ids=chunk_ids,
                        metadatas=chunk_metadatas
                )
                print(f"HNSW RAG built successfully with {len(large_chunks)} chunks")

        print("PDF loaded successfully into both RAG systems!")
        print("="*DIVIDE)
        
        return hnsw_rag, crossranking_rag

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

def query_rag(rag, query: str, top_k: int = 10):
        start_time = time.time() # za merenje vremena
        print("="*80)
        print(f"QUERY: {query} for {rag.__class__.__name__}")
        results = rag.retrieve(query, top_k=top_k)

        # queryujemo LLM
        response = generate_response(query, results['documents'])
        print(f"Response: {response}")
        for i, metadata in enumerate(results['metadatas']):
                print(f"  Metadata: {format_metadata(metadata)}")
        for i, document in enumerate(results['documents']):
                print(f"  Document {i}: {document}...")
        end_time = time.time()
        print(f"Time taken: {end_time - start_time:.2f} seconds")
        print("="*80)


def main():
        # dodamo pdf u oba raga
        crossranking_rag, hnsw_rag = load_pdf_into_rags()
        # prvo hnsw rag
        for query in QUESTIONS:
                query_rag(crossranking_rag,query)
        # for query in QUESTIONS:
        #         query_rag(crossranking_rag,query,top_k=5)
                

if __name__ == "__main__":
        main()
