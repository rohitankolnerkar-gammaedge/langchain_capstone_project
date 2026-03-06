from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.schema import Document

def split_documents(documents: list[Document]) -> list[Document]:
    

    if not documents:
        print("Warning: No documents to split!")
        return []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = text_splitter.split_documents(documents)
    
    if not chunks:
        print("Warning: Split resulted in no chunks!")

    
    print(f"Total chunks created: {len(chunks)}")
    print(f"Type of chunks: {type(chunks)}")
    if chunks:
        print(f"Sample chunk content:\n{chunks[0].page_content[:500]}...")
    
    
    return chunks