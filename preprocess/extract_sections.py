import os
import PyPDF2
import pandas as pd
from typing import Dict, List, Optional
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PaperProcessor:
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.papers_df = pd.read_csv(f'{base_path}/raw/geospatial_papers.csv')
        
    def extract_text_from_pdf(self, file_path: str) -> Optional[str]:
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            logger.error(f"Error processing {file_path}: {str(e)}")
            return None

    def identify_sections(self, text: str) -> Dict[str, str]:
        sections = {}
        
        # Common section headers in academic papers
        section_patterns = {
            'abstract': r'(?i)abstract.*?\n(.*?)(?=\n(?:introduction|1\.|\d\.|keywords))',
            'introduction': r'(?i)(?:1\.|1\s+)?introduction.*?\n(.*?)(?=\n(?:2\.|related work|\d\.))',
            'methodology': r'(?i)(?:3\.|method|methodology|approach).*?\n(.*?)(?=\n(?:\d\.|results|evaluation|experiments))',
            'training': r'(?i)(?:training|implementation details).*?\n(.*?)(?=\n(?:\d\.|evaluation|results|experiments))',
            'evaluation': r'(?i)(?:evaluation|experiments|results).*?\n(.*?)(?=\n(?:\d\.|conclusion|discussion))'
        }
        
        for section, pattern in section_patterns.items():
            match = re.search(pattern, text, re.DOTALL)
            if match:
                sections[section] = match.group(1).strip()
            else:
                sections[section] = ""
                
        return sections

    def process_papers(self) -> List[Dict]:
        processed_papers = []
        
        for _, row in self.papers_df.iterrows():
            if not row['downloaded'] or pd.isna(row['filename']):
                continue
                
            file_path = os.path.join(self.base_path, 'raw/downloaded_papers', row['filename'])
            if not os.path.exists(file_path):
                logger.warning(f"File not found: {file_path}")
                continue
                
            logger.info(f"Processing paper: {row['title']}")
            text = self.extract_text_from_pdf(file_path)
            
            if text:
                sections = self.identify_sections(text)
                paper_info = {
                    'metadata': {
                        'title': row['title'],
                        'model_name': row['model_name'],
                        'publication': row['publication']
                    },
                    'sections': sections
                }
                processed_papers.append(paper_info)
                
        return processed_papers

def main():
    base_path = "../data/papers"
    processor = PaperProcessor(base_path)
    processed_papers = processor.process_papers()
    
    # Save processed results
    import json
    with open(f'{base_path}/processed/extracted_papers.json', 'w') as f:
        json.dump(processed_papers, f, indent=2)

if __name__ == "__main__":
    main()