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
        
    def extract_chapters_and_subchapters(self) -> List[Dict]:
        """
        Extract chapters and subchapters from the PDF using document structure.
        Returns a list of dictionaries with content and metadata.
        """
        chapters = []
        current_chapter = None
        current_subchapter = None
        current_title = None
        current_content = []
        current_page = 1
        start_page = 1
        
        for element in self.elements:
            # Get metadata
            metadata = element.metadata if hasattr(element, 'metadata') else None
            page_num = metadata.page_number if metadata and hasattr(metadata, 'page_number') else current_page
            
            if page_num != current_page:
                current_page = page_num
            
            text = str(element).strip()
            
            # chapter i skecije
            # "1", "1.1", "1.1.1", etc.
            section_match = re.match(r'^(\d+(?:\s*\.\s*\d+)*)\s*$', text)
            
            if isinstance(element, Title) or section_match:
                if section_match:
                    if current_content and current_chapter is not None:
                        self._save_chapter(chapters, current_chapter, current_subchapter, 
                                         current_title, current_content, start_page, current_page)
                        current_content = []
                    
                    section_num = section_match.group(1).replace(' ', '')
                    parts = section_num.split('.')
                    
                    if len(parts) == 1:
                        # glavni chapter
                        current_chapter = section_num
                        current_subchapter = None
                        current_title = None
                    else:
                        # subchapter
                        current_chapter = parts[0]
                        current_subchapter = section_num
                        current_title = None
                    
                    start_page = page_num
                    
                elif isinstance(element, Title) and not current_title:
                    current_title = text
                    
            elif isinstance(element, (NarrativeText, Text)):
                # Regular content
                if text and len(text) > 10:  # Filter very short texts
                    # Check if this text contains a chapter heading pattern
                    chapter_in_text = re.match(r'^(\d+)\s+(.+)$', text)
                    if chapter_in_text and len(text) < 100:
                        # Save previous section
                        if current_content and current_chapter is not None:
                            self._save_chapter(chapters, current_chapter, current_subchapter,
                                             current_title, current_content, start_page, current_page)
                            current_content = []
                        
                        current_chapter = chapter_in_text.group(1)
                        current_subchapter = None
                        current_title = chapter_in_text.group(2).strip()
                        start_page = page_num
                    else:
                        current_content.append(text)
        
        # Save the last section
        if current_content and current_chapter is not None:
            self._save_chapter(chapters, current_chapter, current_subchapter,
                             current_title, current_content, start_page, current_page)
        
        return chapters
    
    def _save_chapter(self, chapters: List[Dict], chapter: str, subchapter: str,
                      title: str, content: List[str], start_page: int, end_page: int):
        """Helper method to save a chapter/section with metadata."""
        if not content:
            return
            
        # Join content
        full_content = ' '.join(content)
        
        # Use title or first line as title
        if not title:
            title = content[0] if content else "Unknown"
        
        if len(title) > 100:
            title = title[:100] + "..."
        
        chapter_data = {
            'content': full_content,
            'chapter': chapter or "0",
            'chapter_number': chapter or "0",
            'subchapter': subchapter or "",
            'title': title,
            'page_start': start_page,
            'page_end': end_page
        }
        
        chapters.append(chapter_data)
    
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


def test_parser():
    """Test the PDF parser."""
    parser = PDFParser("data/crafting-interpreters.pdf")
    chapters = parser.extract_chapters_and_subchapters()
    print(f"Found {len(chapters)} chapters/subchapters")
    
    if chapters:
        print("\nFirst 5 chapters/subchapters:")
        for i, ch in enumerate(chapters[:5]):
            print(f"\n{i+1}. Chapter {ch['chapter']}" + 
                  (f", Section {ch['subchapter']}" if ch['subchapter'] else ""))
            print(f"   Title: {ch['title']}")
            print(f"   Pages: {ch['page_start']}-{ch['page_end']}")
            print(f"   Content length: {len(ch['content'])} chars")
            print(f"   Content preview: {ch['content'][:150]}...")
    
    print("\n" + "="*80)
    print("Extracting paragraphs...")
    paragraphs = parser.extract_paragraphs()
    print(f"Found {len(paragraphs)} paragraphs")
    
    if paragraphs:
        print("\nFirst 3 paragraphs:")
        for i, para in enumerate(paragraphs[:3]):
            print(f"\n{i+1}. Chapter {para['chapter']}" +
                  (f", Section {para['subchapter']}" if para['subchapter'] else ""))
            print(f"   Page: {para['page_start']}")
            print(f"   Content: {para['content'][:150]}...")
    


if __name__ == "__main__":
    test_parser()
