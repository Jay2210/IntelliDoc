from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_text(text: str) -> list[str]:
    """
    Chunks text using a recursive character splitter with a defined size and overlap.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=300,
        length_function=len,
    )
    chunks = text_splitter.split_text(text)
    return chunks