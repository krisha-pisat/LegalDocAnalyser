import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(dotenv_path=os.path.join(base, ".env"))
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_model = ChatGroq(model="llama3-8b-8192", api_key=GROQ_API_KEY)

prompt_template = """
Use the context provided to answer the user's question.
If unsure, say "I don't know".

Question: {question}
Context: {context}

Answer:
"""

def generate_answer(query: str, docs: list) -> str:
    context = "\n\n".join(doc.page_content for doc in docs)
    prompt  = ChatPromptTemplate.from_template(prompt_template)
    chain   = prompt | groq_model
    result  = chain.invoke({"question": query, "context": context})
    return result.content