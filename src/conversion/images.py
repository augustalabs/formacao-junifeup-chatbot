from openai import OpenAI 
import os
from dotenv import load_dotenv
import base64
import json
from langchain_core.documents import Document
from src.utils import chunking

def describe_image(image_path, metadata):
    """
    Generate a description for an image.
    
    Args:
        image_path (str): Path to the image file.
        metadata (dict): Metadata for the file.
        
    Returns:
        list: List with a single document containing the image description.
    """
    print(f"Describing image: {image_path}")
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    try:
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        content = [{"type": "text", "text": "Analyze this image in detail and provide a thorough description of what is shown."}]
        
        # Append image to the content list
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}",
                "detail": "low"
            }
        })
        
        messages = [
            {
                "role": "system",
                "content": "You are an image analyzer and your job is to make a very detailed analysis of all the images presented and describe every single detail as thoroughly as possible."
            },
            {
                "role": "user",
                "content": content
            }
        ]
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "column_validation_response",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                            }
                        },
                        "required": ["description"],
                        "additionalProperties": False
                    }
                }
            }
        )
        
        result = json.loads(response.choices[0].message.content)
        description = result['description']
        

        doc = Document(
            page_content=description,
            metadata=metadata
        )
        
        # Update metadata to indicate this is an image description
        metadata.update({'content_type': 'image_description'})
        chunks = chunking([doc], metadata)
        print(f"Created {len(chunks)} chunks from image description")
        
        return chunks
    
    except Exception as e:
        print(f"Error describing image: {e}")
        return []