"""
PDF Parser for extracting chapters, subchapters, and paragraphs with metadata.
Uses the unstructured library for better document structure detection.
"""

from typing import List, Dict
from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import Title, NarrativeText, Text
from unstructured.chunking.basic import chunk_elements
import re

MIN_PARAGRAPH_LENGTH = 50
CHUNK_SIZE = 4

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
    
    
    def extract_fixed_size_chunks(self, chunk_size: int = 512, overlap: int = 64) -> List[Dict]:
        """
        Extracts fixed-size text chunks from the PDF elements using unstructured library.
        """
        chunks = chunk_elements(self.elements, max_characters=chunk_size, new_after_n_chars=chunk_size, overlap=overlap)
        
        formatted_chunks = []
        
        for chunk in chunks:
            metadata = chunk.metadata.to_dict() if hasattr(chunk, 'metadata') else {}
            
            chapter = "0"
            chapter_number = "0"
            subchapter = ""
            page_start = metadata.get('page_number', 1)
            
            
            formatted_chunks.append({
                'content': str(chunk),
                'chapter': str(chapter),
                'chapter_number': str(chapter_number),
                'subchapter': subchapter,
                'page_start': page_start,
                'page_end': page_start # chunk je uglavnom na jednom pageu
            })
            
        return formatted_chunks

    def extract_paragraphs(self) -> List[Dict]:
        """
        Uzima paragrafe iz PDFa
        """
        paragraphs = []
        current_chapter = "0"
        current_subchapter = None
        current_page = 1
        
        for element in self.elements:
            # metadata
            metadata = element.metadata if hasattr(element, 'metadata') else None
            page_num = metadata.page_number if metadata and hasattr(metadata, 'page_number') else current_page
            
            if page_num != current_page:
                current_page = page_num
            
            text = str(element).strip()
            
            # chapter i skecije
            # "1", "1.1", "1.1.1", etc.
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
            
            # paragrafi
            if isinstance(element, (NarrativeText, Text)):
                # ne dodajemo kratke tekstove
                if len(text) > MIN_PARAGRAPH_LENGTH:
                    
                    paragraphs.append({
                        'content': text,
                        'chapter': current_chapter,
                        'chapter_number': current_chapter,
                        'subchapter': current_subchapter or "",
                        'page_start': page_num,
                        'page_end': page_num
                    })
        
        return paragraphs
