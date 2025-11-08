from disable_warnings import disable_warning_messages
disable_warning_messages()
import os
from rag import RAG
from groq import Groq

API_KEY = os.environ.get("GROQ_API_KEY")
MODEL = "llama-3.3-70b-versatile"

def generate_response(query: str,context: str) -> str:
        prompt = f"""
        You are a helpful assistant that can answer questions about the following context:
        {context}
        Question: {query}
        Answer:
        """
        response = Groq(api_key=API_KEY).chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
        )
        return response.choices[0].message.content

def main():
        rag = RAG()
        results = rag.retrieve(query="What is Machine Learning?")
        print(results)
        response = generate_response(query="What is machine learning?",context=results["documents"][0])
        print(response)

if __name__ == "__main__":
        main()