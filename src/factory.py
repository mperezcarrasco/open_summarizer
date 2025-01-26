from langchain_ollama import ChatOllama
from sentence_transformers import CrossEncoder
from src.core.analyzer import PaperAnalyzer
from src.retrieval.retriever import Retriever 
from src.retrieval.summarizer import RCSummarizer
from src.prompts.templates import PromptTemplates
from src.embeddings.vectorstore import VectorStore

class AnalyzerFactory:
   @staticmethod
   def create_analyzer(config):
       templates = PromptTemplates(config.get("llm")["model_name"])
       
       llm = ChatOllama(
           model=config.get("llm")["model"],
           temperature=config.get("llm")["temperature"],
           seed=config.get("llm")["seed"],
           num_gpu=1
       )
       
       embeddings = VectorStore(
           model_name=config.get("vectorstore")["model"],
           device=config.get("vectorstore")["device"],
           data_path=config.get("vectorstore")["path"]
       )
       
       cross_encoder = CrossEncoder(config.get("cross_encoder")["model"])
       
       summarizer = RCSummarizer(llm, templates)
       retriever = Retriever(embeddings, summarizer, cross_encoder)
       
       return PaperAnalyzer(retriever, llm, templates)