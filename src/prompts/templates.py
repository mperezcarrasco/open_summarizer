from typing import Dict
from .configs import PAPER_ANALYSIS_ASPECTS

class PromptTemplates:
    def __init__(self, model_name: str):
        self.model_name = model_name.lower()
        self.templates = self._get_templates()
        self.aspects = PAPER_ANALYSIS_ASPECTS

    def _get_templates(self) -> Dict:
        if "llama" in self.model_name:
            return {
                'rcs': """[INST] You are a knowledgeable research assistant.
Summarize key information to address the given question based on the provided excerpt.
Then, evaluate the relevance of your summary.

Format your response as a JSON object with the following fields:
{{
  "summary": "Concise summary of up to 200 words.",
  "relevance_score": "<0-10>: Assign an integer score indicating relevance."
}}

Excerpt: {chunk}
Question: {query}

Provide only the JSON object in your response.[/INST]""",

                'analysis': """[INST] You are a skilled research assistant.
Analyze the provided summaries and extract useful insights to answer the question below.

Question: {query}

List of Summaries:
{paper_excerpts}

Return your response as a JSON object with the following structure:
{fields}

Provide only the JSON object in your response.[/INST]"""
            }
        
        elif "deepseek" in self.model_name:
            return {
                'rcs': """<|system|>
You are an analytical research assistant.
Summarize relevant details from the given excerpt to answer the question.
Then, evaluate the relevance of your summary.

Provide the output as a JSON object with these fields:
{{
  "summary": "Concise summary of up to 200 words.",
  "relevance_score": "<0-10>: Assign an integer score indicating relevance."
}}

Excerpt: {chunk}
Query: {query}</s>

Output only the JSON object.""",

                'analysis': """<|system|>
Analyze the provided summaries and extract critical insights to address the question.

Question: {query}

List of Summaries:
{paper_excerpts}

Your response must strictly follow this JSON structure:
{fields}</s>

Output only the JSON object."""
            }
        
        else:
            raise ValueError("Unsupported model name. Please specify either 'llama' or 'deepseek'.")

    def get_prompt(self, prompt_type: str, **kwargs) -> str:
        template = self.templates.get(prompt_type)
        if not template:
            raise ValueError(f"Unknown prompt type: {prompt_type}")
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required parameter: {e}") from e