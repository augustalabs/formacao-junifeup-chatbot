from datetime import datetime
import json
import os
from openai import OpenAI
import pinecone

def retrieve_context(query: str, topk: int = 20, filters: dict = {}) -> str:
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    pc = pinecone.Pinecone(api_key=os.getenv('PINECONE_API_KEY'))

    # Create embedding for the query
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=query
    )
    embedded_query = response.data[0].embedding

    # Pinecone query
    index = pc.Index('formacao-drive-documents')
    
    retrieval = index.query(
        vector=embedded_query,
        top_k=topk,
        include_values=True,
        include_metadata=True,
        filter=filters
    )
    
    # Format context with text format
    context_parts = []
    for i, match in enumerate(retrieval['matches'], 1):
        metadata = match['metadata']
        text_content = metadata['text']
        
        formatted_chunk = (
            f"<INFO NUMBER {i}>\n"
            f"{text_content}\n"
        )
        context_parts.append(formatted_chunk)
        
    # Join with double newlines for better separation
    context = "Context:\n\n" + "\n\n".join(context_parts)

    return context

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    
    print(retrieve_context('funcionalidade Operator', topk=10))