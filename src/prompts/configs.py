PAPER_ANALYSIS_ASPECTS = {
   'basic_info': {
       'query': "What is the paper about? What are the details and machine learning tasks addressed in the paper? put spectial focus on model name, general summary, problem statement and tasks it solves",
       'prompt': """Extract:
       1. Model name (proposed method name)
       2. General Summary
       3. Problem statement
       4. Tasks solved
       
       Format as JSON: {model_name, summary, tasks, problem_statement}
       Use 'Not specified' if missing."""
   },
   'method': {
       'query': "What is the method, technical approach, methodology and architecture the paper proposes? put spectial focus on architecture, training procedure (dataset and methodology used for training), key innovations, and implementation details.", 
       'prompt': """Extract technical details:
       1. Architecture 
       2. Training procedure: adressing what dataset and methodology they used for training
       3. Key innovations
       4. Implementation details
       
       Format as JSON: {architecture, training_procedure, key_innovations, implementation_details}
       Use 'Not specified' if missing."""
   },
   'experiments': {
       'query': "What experiments and results are presented? put spectial focus on datasets, baselines, metrics, results, and hardware.",
       'prompt': """Extract experimental details:
       1. Datasets
       2. Baselines
       3. Metrics
       4. Results (with numbers)
       5. Hardware
       
       Format as JSON: {datasets, baselines, metrics, results, hardware}
       Use 'Not specified' if missing."""
   }
}