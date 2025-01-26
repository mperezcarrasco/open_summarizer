import yaml
import json
import logging
from pathlib import Path

class Config:
   def __init__(self, config_path: str = "config.yaml"):
       self.config = self._load_config(config_path)

   def _load_config(self, path):
       with open(path) as f:
           return yaml.safe_load(f)

   def get(self, key, default=None):
       return self.config.get(key, default)

def setup_logger(name: str, log_path: str = "logs"):
   Path(log_path).mkdir(exist_ok=True)
   
   logger = logging.getLogger(name)
   logger.setLevel(logging.INFO)

   formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
   
   file_handler = logging.FileHandler(f"{log_path}/{name}.log")
   file_handler.setFormatter(formatter)
   logger.addHandler(file_handler)

   return logger

class FileHandler:
   @staticmethod
   def save_json(data, filepath):
       Path(filepath).parent.mkdir(parents=True, exist_ok=True)
       with open(filepath, 'w') as f:
           json.dump(data, f, indent=2)

   @staticmethod
   def load_json(filepath):
       with open(filepath) as f:
           return json.load(f)