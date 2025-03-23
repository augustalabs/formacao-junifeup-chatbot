import os
from datetime import datetime
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain_openai.embeddings import OpenAIEmbeddings
import pinecone
from langchain_pinecone import PineconeVectorStore

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')

def chunking(pages, metadata, chunk_size=700, chunk_overlap=50):
    # Apply metadata to all pages before chunking
    for page in pages:
        page.metadata.update(metadata)
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_documents(pages)
    
    # The metadata should be preserved in each chunk automatically
    return chunks

def load_to_vdb(chunks, index_name='formacao-drive-documents'):
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    
    # Initialize Pinecone client
    pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
    
    # Initialize the index
    index = pc.Index(index_name)
    
    # Create a PineconeVectorStore instance (using updated import)
    vector_store = PineconeVectorStore(index=index, embedding=embeddings, text_key="text")
    
    # Batch insert the chunks into the vector store
    batch_size = 100  # Define your preferred batch size
    for i in range(0, len(chunks), batch_size):
        chunk_batch = chunks[i:i + batch_size]
        vector_store.add_documents(chunk_batch)

if __name__ == '__main__':
    for root, _, files in os.walk('docs'):
        for filename in files:
            if filename.endswith('.pdf'):
                file_path = os.path.join(root, filename)
                
                # Create metadata dictionary
                metadata = {
                    'filename': filename,
                    'filepath': file_path,
                    'upload_time': datetime.now().isoformat(),
                    'file_size': os.path.getsize(file_path),
                    'file_type': 'pdf',
                    'relative_path': os.path.relpath(file_path, 'docs')
                }
                
                # Load PDF
                loader = PyPDFLoader(file_path)
                pages = loader.load()
                
                # Process with metadata
                chunks = chunking(pages, metadata)
                load_to_vdb(chunks)
                
                print(f"Processed {filename} with {len(chunks)} chunks and metadata")