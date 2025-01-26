import pandas as pd
import re

def extract_table_sections(markdown_content):
    sections = {
        'Vision': re.findall(r'## Remote Sensing.*?Vision.*?Foundation Models\n\n\|.*?\|(.*?)(?=\n\n##)', markdown_content, re.DOTALL),
        'Vision-Language': re.findall(r'## Remote Sensing.*?Vision-Language.*?Foundation Models\n\n\|.*?\|(.*?)(?=\n\n##)', markdown_content, re.DOTALL),
        'Generative': re.findall(r'## Remote Sensing.*?Generative.*?Foundation Models\n\n\|.*?\|(.*?)(?=\n\n##)', markdown_content, re.DOTALL),
        'Vision-Location': re.findall(r'## Remote Sensing.*?Vision-Location.*?Foundation Models\n\n\|.*?\|(.*?)(?=\n\n##)', markdown_content, re.DOTALL),
        'Task-specific': re.findall(r'## Remote Sensing.*?Task-specific.*?Foundation Models\n\n\|.*?\|(.*?)(?=\n\n##)', markdown_content, re.DOTALL)
    }
    return sections

def parse_table_row(row):
    parts = [part.strip() for part in row.split('|')]
    if len(parts) >= 5:
        # Extract paper link and code link
        paper_link = re.findall(r'\[(.*?)\]\((.*?)\)', parts[4])
        code_link = re.findall(r'\[(.*?)\]\((.*?)\)', parts[5]) if len(parts) > 5 else None
        
        return {
            'model_name': parts[1].replace('**', ''),
            'title': parts[2].replace('**', ''),
            'publication': parts[3],
            'paper_link': paper_link[0][1] if paper_link else '',
            'code_link': code_link[0][1] if code_link else 'N/A',
            'model_type': ''  # Will be filled later
        }
    return None

def process_markdown_to_csv(markdown_content):
    sections = extract_table_sections(markdown_content)
    all_papers = []
    
    for section_name, content in sections.items():
        if not content:
            continue
            
        rows = content[0].strip().split('\n')
        for row in rows:
            if '|' not in row or '---' in row:
                continue
                
            paper_info = parse_table_row(row)
            if paper_info:
                paper_info['model_type'] = section_name
                all_papers.append(paper_info)
    
    # Convert to DataFrame and save to CSV
    df = pd.DataFrame(all_papers)
    return df

# Read the markdown content
with open('../data/papers/raw/papers_geospatial.md', 'r', encoding='utf-8') as file:
    markdown_content = file.read()

# Process and save to CSV
df = process_markdown_to_csv(markdown_content)
print(f"Extracted {len(df)} papers")
print("\nSample of extracted data:")
print(df.head())

df.to_csv('../data/papers/raw/geospatial_papers.csv', index=False)