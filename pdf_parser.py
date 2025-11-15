"""
PDF Parser for extracting chapters, subchapters, and paragraphs with metadata.
Uses the unstructured library for better document structure detection.
"""

from typing import List, Dict
from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import Title, NarrativeText, Text
import re


class PDFParser:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        # nema slika i tabela
        self.elements = partition_pdf(
            filename=pdf_path,
            strategy="fast",  
            infer_table_structure=False,  
            extract_images_in_pdf=False,
            include_page_breaks=True
        )
        print(f"Total elements from PDF: {len(self.elements)}")
        
    def extract_large_chunks(self, paragraphs_per_chunk: int = 4) -> List[Dict]:
        """
        Extract larger chunks by combining multiple paragraphs.
        This creates bigger context windows for the HNSW RAG.
        
        Args:
            paragraphs_per_chunk: Number of paragraphs to combine into one chunk
        
        Returns:
            List of dictionaries with combined content and metadata.
        """
        # First get all paragraphs
        paragraphs = self.extract_paragraphs()
        
        large_chunks = []
        i = 0
        
        while i < len(paragraphs):
            # Take next N paragraphs
            chunk_paras = paragraphs[i:i + paragraphs_per_chunk]
            
            # Combine their content
            combined_content = ' '.join([p['content'] for p in chunk_paras])
            
            # Use metadata from first paragraph in chunk
            first_para = chunk_paras[0]
            last_para = chunk_paras[-1]
            
            chunk_data = {
                'content': combined_content,
                'chapter': first_para['chapter'],
                'chapter_number': first_para['chapter_number'],
                'subchapter': first_para.get('subchapter', ''),
                'page_start': first_para['page_start'],
                'page_end': last_para['page_end'],
                'num_paragraphs': len(chunk_paras)
            }
            
            large_chunks.append(chunk_data)
            i += paragraphs_per_chunk
        
        return large_chunks
    
    def extract_paragraphs(self) -> List[Dict]:
        """
        Extract paragraphs from the PDF.
        Returns a list of dictionaries with paragraph content and metadata.
        """
        paragraphs = []
        current_chapter = "0"
        current_subchapter = None
        current_page = 1
        
        for element in self.elements:
            # Get metadata
            metadata = element.metadata if hasattr(element, 'metadata') else None
            page_num = metadata.page_number if metadata and hasattr(metadata, 'page_number') else current_page
            
            if page_num != current_page:
                current_page = page_num
            
            text = str(element).strip()
            
            # Track chapter context from section numbers
            section_match = re.match(r'^(\d+(?:\s*\.\s*\d+)*)\s*$', text)
            if section_match:
                section_num = section_match.group(1).replace(' ', '')
                parts = section_num.split('.')
                if len(parts) == 1:
                    current_chapter = section_num
                    current_subchapter = None
                else:
                    current_chapter = parts[0]
                    current_subchapter = section_num
                continue
            
            # Extract narrative text as paragraphs
            if isinstance(element, (NarrativeText, Text)):
                # Filter out very short texts, page numbers, and section numbers
                if (len(text) > 50 and 
                    not re.match(r'^\d+$', text) and
                    not re.match(r'^(\d+\s*\.\s*)+\d*$', text)):
                    
                    paragraphs.append({
                        'content': text,
                        'chapter': current_chapter,
                        'chapter_number': current_chapter,
                        'subchapter': current_subchapter or "",
                        'page_start': page_num,
                        'page_end': page_num
                    })
        
        return paragraphs
