import json
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class RCSummarizer:
    """Retrieval and Contextual Summarization (RCS) implementation.
    
    Reference: Language agents achieve superhuman synthesis of scientific knowledge
    paper: https://arxiv.org/pdf/2409.13740
    """
    def __init__(self, llm, prompt_templates):
        self.llm = llm
        self.templates = prompt_templates

    def summarize(self, query: str, chunk: str) -> Dict:
        """Generate contextual summary of a text chunk relative to query."""
        prompt = self.templates.get_prompt('rcs', chunk=chunk, query=query)
        messages = [{"role": "system", "content": prompt}]
        
        try:
            response = self.llm.invoke(messages)
            response = self._parse_json(response.content)
            self._validate_summary(response)
            return response
            
        except Exception as e:
            logger.warning(f"Failed to generate summary: {str(e)}")
            return {
                "summary": "",
                "relevance_score": "0",
                }

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

    def _validate_summary(self, summary: Dict) -> None:
       """Validate summary has required fields."""
       required_fields = ["summary", "relevance_score"]
       for field in required_fields:
           if field not in summary:
               raise ValueError(f"Missing required field: {field}")
       if field=="relevance_score":
            float(summary["relevance_score"])