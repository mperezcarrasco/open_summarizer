from typing import Dict, Optional, List
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PaperAnalyzer:
    def __init__(self, retriever, llm, prompt_templates):
        self.retriever = retriever
        self.llm = llm
        self.templates = prompt_templates

    def analyze_paper(self, title: str, pdf_path: str = None) -> Dict:
        if pdf_path:
           temp_db = self.retriever.vector_store.create_temp_index(
               pdf_path=pdf_path,
               title=title,
               metadata={
                   "source": "user_upload",
                   "analysis_type": "single_pdf"
               }
           )
           self.retriever.vector_store.db = temp_db
        
        analysis = {}
        for aspect, config in self.templates.aspects.items():
            # Retrieve relevant chunks
            contexts = self.retriever.retrieve_and_rerank(
                query=config['query'], 
                paper_title=title
            )
            # Format prompt with paper title
            formatted_prompt = self.templates.get_prompt(
                'analysis',
                query = config['query'],
                paper_excerpts=' '.join(contexts),
                title=title,
                fields=config['prompt'] 
            )
            
            # Generate analysis
            messages = [{"role": "system", "content": formatted_prompt}]
            response = self.llm.invoke(messages)            
            # Parse response
            try:
                content = str(response.content)
                analysis[aspect] = self._parse_json(content)
            except Exception as e:
                logger.error(f"Failed to analyze {aspect}: {str(e)}")
                analysis[aspect] = {"error": str(e)}
        return analysis

    def _parse_json(self, content: str) -> Dict:
        try:
            # Handle markdown code blocks
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            else:
                json_str = content.strip()

            # Handle newlines
            if "{\n" in json_str:
                json_str = json_str[json_str.find("{\n"):]
                
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {str(e)}")
            return {"error": "Failed to parse JSON", "raw": content}