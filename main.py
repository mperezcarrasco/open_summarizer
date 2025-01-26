from langchain_ollama import ChatOllama
from sentence_transformers import CrossEncoder
from src.core.analyzer import PaperAnalyzer
from src.retrieval.retriever import Retriever 
from src.retrieval.summarizer import RCSummarizer
from src.prompts.templates import PromptTemplates
from src.embeddings.vectorstore import VectorStore
from src.utils.utils import Config, FileHandler, setup_logger

import pandas as pd

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

def main():
   papers = pd.read_csv('./data/papers/raw/geospatial_papers.csv')
   papers = papers[(papers['downloaded']) & (papers['model_type']=="Generative")]
   config = Config("configs/config.yaml")
   analyzer = AnalyzerFactory.create_analyzer(config)
   for _, paper in papers.iterrows():
       results = analyzer.analyze_paper(paper["title"])
       file_mannager = FileHandler()
       model_name = results["basic_info"]["model_name"]
       file_mannager.save_json(results, f"results/{model_name}_results.json")

if __name__ == "__main__":
   main()