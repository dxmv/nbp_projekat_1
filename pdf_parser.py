"""
PDF Parser for extracting chapters, subchapters, and paragraphs with metadata.
Uses the unstructured library for better document structure detection.
"""

from typing import List, Dict
from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import Title, NarrativeText, Text
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
        
    def extract_large_chunks(self) -> List[Dict]:
        """
        Korsiti paragrafe od donje funkcije i kombinuj ih u chunkove od 4 paragrafa
        """
        # svi paragrafi
        paragraphs = self.extract_paragraphs()
        
        large_chunks = []
        i = 0
        
        while i < len(paragraphs):
            # n sledecih paragrafa
            chunk_paras = paragraphs[i:i + CHUNK_SIZE]
            
            combined_content = ' '.join([p['content'] for p in chunk_paras])
            
            # metadata prvog paragrafa u chunku
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
            i += CHUNK_SIZE
        
        return large_chunks
    
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
                # ne dodajemo kratke tekstove, bro
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
