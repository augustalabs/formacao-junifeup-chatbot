from openai import OpenAI 
import os
from dotenv import load_dotenv
import base64
import json

def describe_image(paths):
    base64_images = []
    for path in paths:
        with open(path, "rb") as image_file:
            base64_images.append(base64.b64encode(image_file.read()).decode('utf-8'))
    
    content = [{"type": "text", "text": "Analise detalhadamente esta imagem e fornece uma descrição meticulosa do que está na mesma"}]
    
    # Append all images to the content list
    for base64_image in base64_images:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}",
                "detail": "low"
            }
        })

    messages=[
        {
        "role": "system",
        "content": "You are an image analyzer and your job is to make a very detailed analysis of all the images presented and describe every single detail as thoroughly as possible."
        },
        {
        "role": "user",
        "content": content
        }
    ]

    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
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
    return result['description']


if __name__ == '__main__':
    load_dotenv()
    print(describe_image(['docs/image.jpeg']))