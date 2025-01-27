import fitz
import re
from typing import List, Dict
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

class PDFProcessor:
   def __init__(self):
       self.text_splitter = RecursiveCharacterTextSplitter(
           chunk_size=1000,
           chunk_overlap=200,
           length_function=len
       )

   def clean_text(self, text: str) -> str:
       text = re.sub(r"(?m)^\s*\d+\s*$", "", text)
       text = re.sub(r"(?m)^.*?(?:http|www|@).*$", "", text) 
       text = re.sub(r"\s+", " ", text)
       return text.strip()

   def extract_text(self, pdf_path: str, title: str, metadata: Dict = None) -> List[Document]:
       documents = []
       doc = fitz.open(pdf_path)

       for page_num, page in enumerate(doc):
           blocks = page.get_text("blocks")
           blocks.sort(key=lambda b: (b[1], b[0]))
           
           text_blocks = []
           for block in blocks:
               text = block[4]
               if not re.search(r"[a-zA-Z]", text):
                   continue
               text_blocks.append(text)

           page_text = " ".join(text_blocks)
           page_text = self.clean_text(page_text)

           if page_text:
               enriched_text = f"[{title}] {page_text}"
               doc_metadata = {
                   "source": pdf_path,
                   "page": page_num + 1,
                   "title": title
               }
               if metadata:
                   doc_metadata.update(metadata)
                   
               documents.append(Document(
                   page_content=enriched_text,
                   metadata=doc_metadata
               ))

       doc.close()
       return self.text_splitter.split_documents(documents)