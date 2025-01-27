from src.utils.utils import Config, FileHandler
from src.factory import AnalyzerFactory

import pandas as pd

def main():
   papers = pd.read_csv('./data/papers/raw/geospatial_papers.csv')
   papers = papers[papers['downloaded']][45:]
   config = Config("configs/config.yaml")
   analyzer = AnalyzerFactory.create_analyzer(config)
   for _, paper in papers.iterrows():
       print("Analizing paper: ", paper["title"])
       results = analyzer.analyze_paper(paper["title"])
       file_mannager = FileHandler()
       model_name = paper["model_name"] if paper["model_name"]!="-" else results["basic_info"]["model_name"]
       file_mannager.save_json(results, f"results/{model_name}_results.json")

if __name__ == "__main__":
   main()