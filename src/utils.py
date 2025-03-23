from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

def chunking(pages, metadata, chunk_size=700, chunk_overlap=50):
    # Apply metadata to all pages before chunking
    for page in pages:
        page.metadata.update(metadata)
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_documents(pages)
    
    # The metadata should be preserved in each chunk automatically
    return chunks

def process_pdf(file_path, metadata):
    """
    Process a PDF file.
    
    Args:
        file_path (str): Path to the PDF file.
        metadata (dict): Metadata for the file.
        
    Returns:
        list: List of chunks.
    """
    print(f"Processing PDF: {file_path}")
    
    # Load PDF
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    
    # Process with metadata
    chunks = chunking(pages, metadata)
    print(f"Created {len(chunks)} chunks from {file_path}")
    
    return chunks