from src.vdb.retriever import retrieve_context
import os
from openai import OpenAI

def qa(question):
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    context = retrieve_context(
                question,
                topk=10
            )

    role = """
    You are a chatbot and you take user questions and answer them given the context provided
    """
    
    prompt = f"""
    Here you have the following information as context: 
    {context}
    
    Answer this question: {question}
    You should only use the above question and nothing more
    """
    
    # Set up the API request
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": role},
            {"role": "user", "content": prompt}
        ],
        temperature = 0.2
        )
    
    return response.choices[0].message.content

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    print(qa('O que é o Operator'))