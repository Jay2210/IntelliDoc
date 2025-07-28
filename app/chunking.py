from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=300,
    length_function=len
)

def chunk_text(text: str) -> List[str]:
    return splitter.split_text(text)
