from typing import Dict
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from ..utils.pdf_preprocessor import PDFProcessor

class VectorStore:
    def __init__(self, model_name, device, data_path="./data/papers/processed/"):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": device}
        )
        self.db = FAISS.load_local(data_path, self.embeddings, allow_dangerous_deserialization=True)

    def create_temp_index(self, pdf_path: str, title: str, metadata: Dict = None):
        processor = PDFProcessor()
        chunks = processor.extract_text(pdf_path, title, metadata)
        return FAISS.from_documents(chunks, self.embeddings)