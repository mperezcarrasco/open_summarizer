# Open Paper Summarizer
A Python implementation to test DeepSeek-r1:8b capabilities by reproducing key components from the PaperQA2 paper (arXiv:2409.13740). This implementation focuses on local paper analysis using RAG (Retrieval-Augmented Generation) and RCS (Reranking and Contextual Summarization).

**Note**

This is a partial implementation focused on testing deepseek capabilities. 

**Key differences from PaperQA2**:

- No internet paper search (works only with uploaded PDFs)
- No citation traversal
- Uses deepseek-r1 instead of GPT models

**Features**

- **RCS Implementation**: Reranking and Contextual Summarization for improved paper understanding
- **RAG-based Knowledge Base**: Local vector store for efficient paper chunk retrieval
- **Structured Analysis**: Extracts key information including:
    - Basic Information (model names, tasks, problem statements)
    - Methods (architecture, training procedures, innovations)
    - Experiments (datasets, baselines, metrics, results)



# Installation
```
# Clone the repository
git clone https://github.com/mperezcarrasco/open_summarizer.git
cd paper-summarizer
```

# Environment Setup

Option 1: Local Installation.

We strongly recommend using a virtual environment. Set up a venv environment with:

```
python3 -m venv hsr
source hsr/bin/activate
pip install -r requirements.txt
```

Option 2: Docker container.

Alternatively, a docker image is contained in `Dockerfile`. For a containerized setup, use the provided Docker scripts:

```
bash build_container.sh
bash run_container.sh
```

Requirements
```
langchain
langchain-community 
langchain-ollama
sentence-transformers
faiss-cpu
pandas
pyyaml
```

# Usage

**Command Line**
```
# Analyze a single PDF
python main.py --path path/to/paper.pdf --title "title of the paper"
```

**Python API**
```
from src.core.analyzer import PaperAnalyzer

# Initialize analyzer
analyzer = PaperAnalyzer(config)

# Analyze paper
results = analyzer.analyze_paper("paper_title", pdf_path="path/to/paper.pdf")

# Print results
print(f"Basic Info: {results['basic_info']}")
print(f"Methods: {results['method']}")
print(f"Experiments: {results['experiments']}")
```

**Architecture**
```
src/
├── core/
│   ├── analyzer.py           # Main analyzer implementation
│   └── controller.py         # LLM controller
├── knowledge/
│   ├── base.py              # Base knowledge store
│   ├── vectorstore.py       # FAISS implementation
│   └── prompts.py           # Prompt templates
├── tools/
│   ├── retriever.py         # Document retrieval
│   └── summarizer.py        # RCS implementation
└── utils/
    ├── logger.py            # Logging utilities
    └── pdf.py               # PDF processing
```

# Contributing

Fork the repository
Create a feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request

# Citation
When using components based on PaperQA2, please cite:
```
@article{skarlinski2024language,
  title={Language Agents Achieve Superhuman Synthesis of Scientific Knowledge},
  author={Skarlinski, Michael D and Cox, Sam and Laurent, Jon M and others},
  journal={arXiv preprint arXiv:2409.13740},
  year={2024}
}
```

# License
This project is licensed under the MIT License - see the LICENSE file for details.
# Acknowledgments
Based on techniques from the PaperQA2 paper
Uses deepseek-r1 model for LLM capabilities
Built with langchain and FAISS for vector storage

# Disclaimer
This is an experimental implementation meant to test deepseek capabilities. It's not meant to be a full reproduction of PaperQA2 and lacks several key features from the original paper.
