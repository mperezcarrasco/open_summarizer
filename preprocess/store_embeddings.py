import os
import pandas as pd
from pathlib import Path
from typing import List
import fitz
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResearchEmbeddingStore:
    def __init__(self):
        self.papers_df = pd.read_csv('../data/papers/raw/geospatial_papers.csv')
        self.papers_df = self.papers_df[self.papers_df['downloaded'] == True]
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cuda"}
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

    def clean_text(self, text: str) -> str:
        text = re.sub(r"(?m)^\s*\d+\s*$", "", text)
        text = re.sub(r"(?m)^.*?(?:http|www|@).*$", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def extract_text_from_pdf(self, pdf_path: str, paper_title: str) -> List[Document]:
        logger.info(f"Processing PDF: {pdf_path}")
        documents = []

        try:
            doc = fitz.open(pdf_path)
            for page_num, page in enumerate(doc):
                blocks = page.get_text("blocks")
                blocks.sort(key=lambda b: (b[1], b[0]))

                text_blocks = []
                for block in blocks:
                    text = block[4]
                    if not re.search(r"[a-zA-Z]", text):
                        continue
                    text_blocks.append(text)

                page_text = " ".join(text_blocks)
                page_text = self.clean_text(page_text)

                if page_text.strip():
                    # Add paper title at the beginning of each chunk
                    enriched_text = f"[{paper_title}] {page_text}"
                    documents.append(
                        Document(
                            page_content=enriched_text,
                            metadata={"source": pdf_path, "page": page_num + 1},
                        )
                    )

            doc.close()
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            return []

        return documents

    def process_papers(self) -> None:
        all_documents = []
        pdf_directory = '../data/papers/raw/downloaded_papers/'
        
        for _, paper in self.papers_df.iterrows():
            pdf_path = Path(pdf_directory) / paper['filename']
            if not pdf_path.exists():
                continue
                
            documents = self.extract_text_from_pdf(str(pdf_path), paper['title'])
            
            for doc in documents:
                doc.metadata.update({
                    'title': paper['title'],
                    'model_name': paper['model_name'],
                    'publication': paper['publication'],
                    'model_type': paper['model_type'],
                    'paper_link': paper['paper_link']
                })
            
            all_documents.extend(documents)

        texts = self.text_splitter.split_documents(all_documents)
        db = FAISS.from_documents(texts, self.embeddings)
        db.save_local("../data/papers/processed/")
        logger.info("Vector store saved successfully")

if __name__ == "__main__":
    store = ResearchEmbeddingStore()
    store.process_papers()