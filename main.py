# from disable_warnings import disable_warning_messages
# disable_warning_messages()
import os
from rag import CrossRankingRAG
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
        print("Chunking documents...")
        rag = CrossRankingRAG()
        with open("data/Machine_learning.txt", "r") as file:
                text = file.read()
        rag.chunk_documents(documents=[text])
        print("Documents chunked, added and embedded\n")
        query = "What is Machine Learning?"
        results = rag.retrieve(query=query)
        for k,v in results.items():
                for val in v:
                        print(val)
                print("="*100)
                print("\n")
        response = generate_response(query=query,context=results["documents"][0])
        print(response)

if __name__ == "__main__":
        main()