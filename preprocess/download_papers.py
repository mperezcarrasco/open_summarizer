import pandas as pd
import requests
import os
from urllib.parse import urlparse
from pathlib import Path
import arxiv
import hashlib
from difflib import SequenceMatcher
from datetime import datetime
import re

def get_arxiv_id_from_url(url):
    """Extract arxiv ID from URL if present."""
    if 'arxiv' not in url.lower():
        return None
    try:
        # Handle different arxiv URL formats
        parts = url.split('/')
        arxiv_id = next(p for p in reversed(parts) if p and any(c.isdigit() for c in p))
        return arxiv_id.split('v')[0]  # Remove version number if present
    except:
        return None

def clean_title(title):
    """Clean title for comparison."""
    return re.sub(r'[^\w\s]', '', title.lower())

def calculate_similarity(str1, str2):
    """Calculate similarity between two strings."""
    return SequenceMatcher(None, clean_title(str1), clean_title(str2)).ratio()

def verify_arxiv_paper(arxiv_paper, original_paper):
    """Verify if arxiv paper matches the original paper."""
    title_similarity = calculate_similarity(arxiv_paper.title, original_paper['title'])
    
    # Check publication date if available
    if 'year' in original_paper:
        try:
            arxiv_year = arxiv_paper.published.year
            if abs(int(original_paper['year']) - arxiv_year) > 1:
                return False
        except:
            pass
    
    # Strict matching for high confidence
    if title_similarity > 0.95:
        return True
        
    # Medium confidence matching with additional checks
    if title_similarity > 0.8:
        # Check authors if available
        if 'authors' in original_paper and arxiv_paper.authors:
            author_match = any(
                calculate_similarity(author.name, original_paper['authors']) > 0.8
                for author in arxiv_paper.authors
            )
            if author_match:
                return True
    
    return False

def search_paper_on_arxiv(paper):
    """Search for paper on arxiv with verification."""
    try:
        # Search by title
        search = arxiv.Search(
            query=f"ti:\"{paper['title']}\"",
            max_results=5
        )
        results = list(search.results())
        
        # Check each result for match
        for result in results:
            if verify_arxiv_paper(result, paper):
                return result
                
        # If no match, try broader search with model name
        if paper['model_name']:
            search = arxiv.Search(
                query=f"ti:\"{paper['model_name']}\"",
                max_results=5
            )
            results = list(search.results())
            
            for result in results:
                if verify_arxiv_paper(result, paper):
                    return result
        
        return None
        
    except Exception as e:
        print(f"Arxiv search failed for {paper['title']}: {str(e)}")
        return None

def get_file_hash(filepath):
    """Calculate SHA-256 hash of file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def is_duplicate(filepath, downloaded_hashes):
    """Check if file is duplicate based on content hash."""
    if not os.path.exists(filepath):
        return False
    file_hash = get_file_hash(filepath)
    if file_hash in downloaded_hashes:
        return True
    downloaded_hashes.add(file_hash)
    return False

def download_paper(url, output_dir, downloaded_hashes):
    try:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        filename = os.path.basename(urlparse(url).path)
        if not filename.endswith('.pdf'):
            filename += '.pdf'
            
        output_path = os.path.join(output_dir, filename)
        
        if os.path.exists(output_path):
            if is_duplicate(output_path, downloaded_hashes):
                return True, filename
        
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()
        
        if 'application/pdf' not in response.headers.get('content-type', '').lower():
            return False, None
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        if is_duplicate(output_path, downloaded_hashes):
            os.remove(output_path)
            return True, filename
            
        return True, filename
        
    except Exception as e:
        print(f"Failed to download {url}: {str(e)}")
        return False, None

def download_from_arxiv(paper, output_dir, downloaded_hashes):
    try:
        arxiv_id = get_arxiv_id_from_url(paper['paper_link'])
        if not arxiv_id:
            result = search_paper_on_arxiv(paper)
            if not result:
                return False, None
        else:
            search = arxiv.Search(id_list=[arxiv_id])
            results = list(search.results())
            if not results:
                return False, None
            result = results[0]
        
        filename = f"{result.get_short_id()}.pdf"
        output_path = os.path.join(output_dir, filename)
        
        if os.path.exists(output_path):
            if is_duplicate(output_path, downloaded_hashes):
                return True, filename
        
        result.download_pdf(dirpath=output_dir, filename=filename)
        
        if is_duplicate(output_path, downloaded_hashes):
            os.remove(output_path)
            return True, filename
            
        return True, filename
        
    except Exception as e:
        print(f"Failed to download from arxiv: {str(e)}")
        return False, None

def main():
    df = pd.read_csv('../data/papers/raw/geospatial_papers.csv')
    
    # Add tracking columns if they don't exist
    if 'downloaded' not in df.columns:
        df['downloaded'] = False
    if 'filename' not in df.columns:
        df['filename'] = ''
    
    output_dir = '../data/papers/raw/'
    downloaded_hashes = set()
    
    total = len(df)
    successful = 0
    failed = []
    
    for index, row in df.iterrows():
        if pd.isna(row['paper_link']):
            failed.append(row['title'])
            continue
            
        print(f"Processing ({index + 1}/{total}): {row['title']}")
        
        # Skip if already downloaded
        if row['downloaded'] and os.path.exists(os.path.join(output_dir, row['filename'])):
            successful += 1
            continue
        
        # Try direct download
        success, filename = download_paper(row['paper_link'], output_dir, downloaded_hashes)
        if success:
            df.at[index, 'downloaded'] = True
            df.at[index, 'filename'] = filename
            successful += 1
            continue
        
        # Try arxiv
        print(f"Attempting arxiv download for: {row['title']}")
        success, filename = download_from_arxiv(row, output_dir, downloaded_hashes)
        if success:
            df.at[index, 'downloaded'] = True
            df.at[index, 'filename'] = filename
            successful += 1
            continue
            
        failed.append(row['title'])
    
    # Save updated CSV
    df.to_csv('../data/papers/raw/geospatial_papers.csv', index=False)
    
    print(f"\nDownload Summary:")
    print(f"Total: {total}")
    print(f"Success: {successful}")
    print(f"Failed: {len(failed)}")
    
    if failed:
        print("\nFailed papers:")
        for title in failed:
            print(title)

if __name__ == "__main__":
    main()