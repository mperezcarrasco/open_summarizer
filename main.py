from src.utils.utils import Config, FileHandler
from src.factory import AnalyzerFactory

import pandas as pd

def main():
   papers = pd.read_csv('./data/papers/raw/geospatial_papers.csv')
   papers = papers[(papers['downloaded']) & (papers['model_type']=="Generative")][3:]
   config = Config("configs/config.yaml")
   analyzer = AnalyzerFactory.create_analyzer(config)
   for _, paper in papers.iterrows():
       results = analyzer.analyze_paper(paper["title"])
       file_mannager = FileHandler()
       model_name = results["basic_info"]["model_name"]
       file_mannager.save_json(results, f"results/{model_name}_results.json")

if __name__ == "__main__":
   main()