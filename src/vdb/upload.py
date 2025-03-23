import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai.embeddings import OpenAIEmbeddings
import pinecone
from langchain_pinecone import PineconeVectorStore
from src.drive.get_files import download_drive_folder_with_service_account
from src.utils import process_pdf
from src.conversion.videos import transcribe_video
from src.conversion.images import describe_image

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
FOLDER_ID = os.getenv('FOLDER_ID')
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')

def get_file_metadata(file_path):
    """
    Generate metadata for a file.
    
    Args:
        file_path (str): Path to the file.
        
    Returns:
        dict: Metadata dictionary.
    """
    filename = os.path.basename(file_path)
    file_extension = os.path.splitext(filename)[1].lower()
    
    # Map file extension to type
    file_type_map = {
        '.pdf': 'pdf',
        '.mp4': 'video',
        '.mov': 'video',
        '.avi': 'video',
        '.mkv': 'video',
        '.jpg': 'image',
        '.jpeg': 'image',
        '.png': 'image',
        '.gif': 'image',
        '.bmp': 'image'
    }
    
    file_type = file_type_map.get(file_extension, 'unknown')
    
    return {
        'filename': filename,
        'filepath': file_path,
        'upload_time': datetime.now().isoformat(),
        'file_size': os.path.getsize(file_path),
        'file_type': file_type,
        'relative_path': os.path.relpath(file_path, 'docs'),
        'extension': file_extension
    }


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


def process_files_and_upload():
    """
    Main function to download files from Google Drive, process them based on type,
    and upload to Pinecone.
    """
    print("Starting document processing pipeline...")
    
    # Download all files from Google Drive
    print("Downloading files from Google Drive...")
    downloaded_files = download_drive_folder_with_service_account(FOLDER_ID, SERVICE_ACCOUNT_FILE)
    print(f"Downloaded {len(downloaded_files)} files in total.")
    
    all_chunks = []
    
    # Process each downloaded file based on its type
    for file_path in downloaded_files:
        # Get file metadata
        metadata = get_file_metadata(file_path)
        file_type = metadata['file_type']
        
        # Process based on file type
        if file_type == 'pdf':
            chunks = process_pdf(file_path, metadata)
            all_chunks.extend(chunks)
        
        elif file_type == 'video':
            chunks = transcribe_video(file_path, metadata)
            all_chunks.extend(chunks)
        
        elif file_type == 'image':
            chunks = describe_image(file_path, metadata)
            all_chunks.extend(chunks)
        
        else:
            print(f"Skipping unsupported file type: {file_path}")
    
    # Upload all processed chunks to Pinecone
    print(f"Uploading {len(all_chunks)} chunks to Pinecone...")
    load_to_vdb(all_chunks)
    
    print("Document processing pipeline completed successfully.")

if __name__ == '__main__':
    process_files_and_upload()