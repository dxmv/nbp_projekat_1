import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import time
from rag import CrossRankingRAG
from hnsw import HnswRAG
from pdf_parser import PDFParser
from groq import Groq


API_KEY = os.environ.get("GROQ_API_KEY")
MODEL = "llama-3.3-70b-versatile"
PDF_PATH = "data/crafting-interpreters.pdf"
DIVIDE = 80

# Defined with Ground Truth data (Chapters for Semantic RAG, Page Ranges for HNSW)
QUESTIONS = [
    {
        "query": "How does the book implement string interning in the hash table, and what performance benefits does this optimization provide?",
        "relevant_chapters": [20],
        "relevant_pages": [[349, 373]]
    },
    {
        "query": "Compare the parsing strategies of jlox and clox: which algorithms are used and how do they represent grammar rules?",
        "relevant_chapters": [6, 17],
        "relevant_pages": [[76, 94], [297, 318]]
    },
    {
        "query": "Why does jlox require a separate 'Resolver' pass before interpretation, and how does it use 'distance' (or hops) to fix the closure binding problem?",
        "relevant_chapters": [11],
        "relevant_pages": [[175, 190]]
    }
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
                return hnsw_rag, crossranking_rag
        
        
        print(f"\nParsing PDF: {PDF_PATH}")
        parser = PDFParser(PDF_PATH)
        
        print("Extracting paragraphs...")
        paragraphs = parser.extract_paragraphs()
        print(f"Found {len(paragraphs)} paragraphs")
        print("Extracting fixed size chunks...")
        large_chunks = parser.extract_fixed_size_chunks()
        print(f"Found {len(large_chunks)} fixed chunks")
        
        # dodajemo paragrafe u crossranking rag
        if len(paragraphs) > 0 and crossranking_count == 0:
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
        if len(large_chunks) > 0 and hnsw_count == 0:
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

def format_metadata(metadata: dict, is_hnsw: bool = False) -> str:
        """Format metadata for display."""
        parts = []
        if is_hnsw:
             if metadata.get('page_start'):
                    parts.append(f"Page {metadata['page_start']}")
        else:
            if metadata.get('chapter'):
                    parts.append(f"Chapter {metadata['chapter']}")
            if metadata.get('subchapter'):
                    parts.append(f"Section {metadata['subchapter']}")
            if metadata.get('page_start'):
                    if metadata.get('page_end') and metadata['page_start'] != metadata['page_end']:
                            parts.append(f"Pages {metadata['page_start']}-{metadata['page_end']}")
                    else:
                            parts.append(f"Page {metadata['page_start']}")
        return " | ".join(parts)

def calculate_metrics(rag, retrieved_metadatas, relevant_chapters, relevant_pages, is_hnsw=False):
        relevant_retrieved = 0
        
        # Helper check for pages
        def is_page_relevant(page_val):
                p = int(page_val)
                for start, end in relevant_pages:
                        if start <= p <= end:
                                return True
                return False

        for meta in retrieved_metadatas:
                if is_hnsw:
                        if is_page_relevant(meta.get('page_start')):
                                relevant_retrieved += 1
                else:
                        try:
                                if int(meta.get('chapter')) in relevant_chapters:
                                        relevant_retrieved += 1
                        except (ValueError, TypeError):
                                pass
                        
        k = len(retrieved_metadatas)
        precision = relevant_retrieved / k if k > 0 else 0
        
        try:
                all_metadatas = rag.collection.get(include=['metadatas'])['metadatas']
                total_relevant = 0
                for meta in all_metadatas:
                        if is_hnsw:
                                if is_page_relevant(meta.get('page_start')):
                                        total_relevant += 1
                        else:
                                try:
                                        if int(meta.get('chapter')) in relevant_chapters:
                                                total_relevant += 1
                                except (ValueError, TypeError):
                                        pass
        except Exception as e:
                print(f"Error calculating recall denominator: {e}")
                total_relevant = 0
                
        recall = relevant_retrieved / total_relevant if total_relevant > 0 else 0
        
        return precision, recall, relevant_retrieved, total_relevant

def query_rag(rag, query_item: dict, top_k: int = 10):
        query = query_item["query"]
        relevant_chapters = query_item.get("relevant_chapters", [])
        relevant_pages = query_item.get("relevant_pages", [])

        start_time = time.time() 
        print("="*80)
        print(f"QUERY: {query} for {rag.__class__.__name__}")
        results = rag.retrieve(query, top_k=top_k)

        # queryujemo LLM
        response = generate_response(query, results['documents'])
        print(f"Response: {response}")
        
        is_hnsw = isinstance(rag, HnswRAG)
        for i, metadata in enumerate(results['metadatas']):
                print(f"  Metadata: {format_metadata(metadata, is_hnsw)}")
        
        # Metrics
        if relevant_chapters or relevant_pages:
                p, r, rel_ret, total_rel = calculate_metrics(
                        rag, 
                        results['metadatas'], 
                        relevant_chapters, 
                        relevant_pages, 
                        is_hnsw
                )
                print("-" * 40)
                print(f"METRICS ({'Pages' if is_hnsw else 'Chapters'} Check)")
                print(f"Precision@{top_k}: {p:.2%}")
                print(f"Recall@{top_k}:    {r:.2%}")
                print(f"Relevant Retrieved: {rel_ret}/{len(results['metadatas'])}")
                print(f"Total Relevant in DB: {total_rel}")
                print("-" * 40)

        end_time = time.time()
        print(f"Time taken: {end_time - start_time:.2f} seconds")
        print("="*80)


def main():
        # dodamo pdf u oba raga
        hnsw_rag, crossranking_rag = load_pdf_into_rags()
        
        for i, query_item in enumerate(QUESTIONS):
                print(f"\n{i+1}. Processing Query: {query_item['query']}")
                query_rag(crossranking_rag, query_item)
                query_rag(hnsw_rag, query_item)
                

if __name__ == "__main__":
        main()
