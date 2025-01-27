from src.utils.utils import Config, FileHandler
from src.factory import AnalyzerFactory
from pathlib import Path
import argparse
import pandas as pd

def analyze_paper_db(config):
   analyzer = AnalyzerFactory.create_analyzer(config)
   papers = pd.read_csv('./data/papers/raw/geospatial_papers.csv')
   papers = papers[papers['downloaded']][52:]
   
   for _, paper in papers.iterrows():
       print("Analizing paper: ", paper["title"])
       results = analyzer.analyze_paper(paper["title"])
       FileHandler.save_json(results, f"results/{paper['model_name']}_results.json")

def analyze_single_pdf(config, pdf_path, title):
   analyzer = AnalyzerFactory.create_analyzer(config)
   results = analyzer.analyze_paper(title, pdf_path)
   FileHandler.save_json(results, f"results/single_pdf_{Path(pdf_path).stem}_results.json")

def main():
   parser = argparse.ArgumentParser()
   parser.add_argument("--path", default=None, help="Path to PDF file")
   parser.add_argument("--title", default=None, help="Paper title (required for single PDF)")
   args = parser.parse_args()

   config = Config("configs/config.yaml")
   
   if args.path:
       if not args.title:
           raise ValueError("Title required for PDF analysis")
       analyze_single_pdf(config, args.path, args.title)
   else:
       analyze_paper_db(config)

if __name__ == "__main__":
   main()