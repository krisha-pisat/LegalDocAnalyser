import json
from langchain.docstore.document import Document

def load_json_and_chunk(
    filepath: str,
    start: int,
    end: int,
    chunk_size: int = 2000,
    overlap: int = 200
) -> list[Document]:
    """
    Load JSON docs [start:end], split their 'content' field into overlapping chunks,
    return as a list of Langchain Documents with metadata.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    subset = data[start:end]
    chunks = []

    for item in subset:
        text = item.get('content', '')
        meta = {k: v for k, v in item.items() if k != 'content'}

        for i in range(0, len(text), chunk_size - overlap):
            piece = text[i : i + chunk_size]
            chunks.append(Document(page_content=piece, metadata=meta))

    return chunks