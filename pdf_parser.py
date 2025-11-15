"""
PDF Parser for extracting chapters, subchapters, and paragraphs with metadata.
"""

import fitz
import re
from typing import List, Dict, Tuple


class PDFParser:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        
    def extract_chapters_and_subchapters(self) -> List[Dict]:
        """
        Extract chapters and subchapters from the PDF.
        Returns a list of dictionaries with content and metadata.
        """
        chapters = []
        current_chapter = None
        current_subchapter = None
        current_content = []
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            text = page.get_text()
            lines = text.split('\n')
            
            for line in lines:
                stripped = line.strip()
                
                # Check if this is a chapter/section number
                section_match = re.match(r'^(\d+)(\s*\.\s*\d+)*\s*$', stripped)
                
                if section_match:
                    section_num = stripped
                    parts = section_num.replace(' ', '').split('.')
                    
                    # Save previous chapter/subchapter if exists
                    if current_content:
                        self._save_section(chapters, current_chapter, current_subchapter, 
                                         current_content, page_num)
                        current_content = []
                    
                    # Determine if this is a chapter or subchapter
                    if len(parts) == 1:
                        # Main chapter
                        current_chapter = section_num
                        current_subchapter = None
                    elif len(parts) == 2:
                        # Subchapter (e.g., 1.1)
                        current_chapter = parts[0]
                        current_subchapter = section_num
                    elif len(parts) >= 3:
                        # Sub-subchapter (e.g., 1.1.1) - treat as subchapter
                        current_chapter = parts[0]
                        current_subchapter = section_num
                else:
                    # Regular content
                    if stripped:
                        current_content.append(stripped)
        
        # Save the last section
        if current_content:
            self._save_section(chapters, current_chapter, current_subchapter, 
                             current_content, len(self.doc) - 1)
        
        return chapters
    
    def _save_section(self, chapters: List[Dict], chapter: str, subchapter: str, 
                      content: List[str], page_num: int):
        """Helper method to save a section with metadata."""
        if not content:
            return
            
        # Join content and create metadata
        full_content = ' '.join(content)
        
        # Try to extract title (usually first significant line)
        title = content[0] if content else "Unknown"
        if len(title) > 100:
            title = title[:100] + "..."
        
        section_data = {
            'content': full_content,
            'chapter': chapter or "0",
            'chapter_number': chapter or "0",
            'subchapter': subchapter or "",  # Ensure no None values
            'title': title,
            'page_end': page_num + 1,
            'page_start': max(1, page_num - len(content) // 50)  # Approximate
        }
        
        chapters.append(section_data)
    
    def extract_paragraphs(self) -> List[Dict]:
        """
        Extract paragraphs from the PDF.
        Returns a list of dictionaries with paragraph content and metadata.
        """
        paragraphs = []
        current_chapter = "0"
        current_subchapter = None
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            text = page.get_text()
            
            # Split into lines and process
            lines = text.split('\n')
            paragraph_lines = []
            
            for line in lines:
                stripped = line.strip()
                
                # Check if this is a section number to track context
                section_match = re.match(r'^(\d+)(\s*\.\s*\d+)*\s*$', stripped)
                if section_match:
                    section_num = stripped.replace(' ', '')
                    parts = section_num.split('.')
                    if len(parts) == 1:
                        current_chapter = section_num
                        current_subchapter = None
                    else:
                        current_chapter = parts[0]
                        current_subchapter = section_num
                    continue
                
                # Build paragraphs
                if stripped:
                    paragraph_lines.append(stripped)
                else:
                    # Empty line - end of paragraph
                    if paragraph_lines and len(paragraph_lines) >= 2:
                        # Create paragraph with metadata
                        paragraph_text = ' '.join(paragraph_lines)
                        
                        # Filter out very short paragraphs and page numbers
                        if len(paragraph_text) > 50 and not re.match(r'^\d+$', paragraph_text):
                            paragraphs.append({
                                'content': paragraph_text,
                                'chapter': current_chapter,
                                'chapter_number': current_chapter,
                                'subchapter': current_subchapter or "",  # Ensure no None values
                                'page_start': page_num + 1,
                                'page_end': page_num + 1
                            })
                    
                    paragraph_lines = []
            
            # Save any remaining paragraph at end of page
            if paragraph_lines and len(paragraph_lines) >= 2:
                paragraph_text = ' '.join(paragraph_lines)
                if len(paragraph_text) > 50:
                    paragraphs.append({
                        'content': paragraph_text,
                        'chapter': current_chapter,
                        'chapter_number': current_chapter,
                        'subchapter': current_subchapter or "",  # Ensure no None values
                        'page_start': page_num + 1,
                        'page_end': page_num + 1
                    })
        
        return paragraphs
    
    def close(self):
        """Close the PDF document."""
        self.doc.close()


def test_parser():
    """Test the PDF parser."""
    parser = PDFParser("data/crafting-interpreters.pdf")
    
    print("Extracting chapters and subchapters...")
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
    
    parser.close()


if __name__ == "__main__":
    test_parser()

