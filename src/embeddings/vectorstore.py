from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

class VectorStore:
    def __init__(self, model_name, device, data_path="./data/papers/processed/"):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": device}
        )
        self.db = FAISS.load_local(data_path, self.embeddings, allow_dangerous_deserialization=True)