import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

base = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(dotenv_path=os.path.join(base, ".env"))
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, api_key=GROQ_API_KEY)

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
    chain   = prompt | llm
    result  = chain.invoke({"question": query, "context": context})
    return result.content