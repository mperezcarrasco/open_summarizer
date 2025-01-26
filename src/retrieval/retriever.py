from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class Retriever:
   def __init__(self, vector_store, summarizer, cross_encoder=None):
       self.vector_store = vector_store
       self.summarizer = summarizer
       self.cross_encoder = cross_encoder
       self.max_results = 200
       self.final_results = 5

   def retrieve_and_rerank(self, query: str, paper_title: str, k: Optional[int] = None) -> List[str]:
       """
       Retrieve relevant chunks and rerank using RCS.
       """
       k = k or self.final_results
       
       # Initial retrieval
       augmented_query = f"[{paper_title}] {query}"
       results = self.vector_store.db.max_marginal_relevance_search(
           augmented_query, 
           k=self.max_results
       )
       
       # Filter for target paper
       filtered_results = [
           doc for doc in results 
           if paper_title == doc.metadata["title"]
       ]
       reranked_results = self.rerank_with_crossencoder(query, filtered_results) if self.cross_encoder is not None \
           else filtered_results
       
       # RCS Step
       contextual_summaries = []
       for doc in reranked_results:
           summary = self.summarizer.summarize(query, doc.page_content)
           if summary["summary"]:
               contextual_summaries.append(summary)
       
       # Rank by relevance score
       ranked_summaries = sorted(
           contextual_summaries,
           key=lambda x: float(x["relevance_score"]),
           reverse=True
       )
       
       # Return top k summaries
       return [summary["summary"] for summary in ranked_summaries[:k]]
   
   def get_metadata(self, paper_chunks: List[Dict]) -> Dict:
        """Get metadata from paper chunks."""
        if not paper_chunks:
            return {}

        # Get first chunk since metadata is same for all chunks from same paper
        metadata = paper_chunks[0].metadata
        
        return {
            'title': metadata.get('title', ''),
            'model_name': metadata.get('model_name', ''),
            'publication': metadata.get('publication', ''),
            'model_type': metadata.get('model_type', ''),
            'paper_link': metadata.get('paper_link', '')
        }
   
   def rerank_with_crossencoder(self, query: str, paper_chunks: List[Dict], k: int = 5) -> List[Dict]:
    """Rerank chunks using cross-encoder."""
    pairs = [[query, doc.page_content] for doc in paper_chunks]
    scores = self.cross_encoder.predict(pairs)
    ranked_results = sorted(zip(paper_chunks, scores), key=lambda x: x[1], reverse=True)
    return [doc for doc, _ in ranked_results[:k]]