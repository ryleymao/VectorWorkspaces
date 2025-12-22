import tiktoken
from typing import List
from app.core.config import settings


def count_tokens(text: str) -> int:
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def chunk_text(text: str, chunk_size: int = None, chunk_overlap: int = None) -> List[str]:
    if chunk_size is None:
        chunk_size = settings.CHUNK_SIZE
    if chunk_overlap is None:
        chunk_overlap = settings.CHUNK_OVERLAP
    
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    
    chunks = []
    start = 0
    
    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
        
        if end >= len(tokens):
            break
        
        start += chunk_size - chunk_overlap
    
    return chunks


def extract_text_from_pdf(file_path: str) -> str:
    try:
        import pdfplumber
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except Exception:
        try:
            import PyPDF2
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
            return text
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")

