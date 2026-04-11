import os
import sys
from datetime import datetime
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import Runnable

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(base_dir)
load_dotenv(dotenv_path=os.path.join(base_dir, ".env"))
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_model = ChatGroq(model="llama-3.3-70b-versatile", api_key=GROQ_API_KEY)

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert Legal AI Assistant. When synthesizing answers from the provided case documents:
1. DIRECTNESS: Answer the user's question directly and concisely. Avoid unnecessary legal interpretations or full case progressions unless explicitly asked.
2. COMPLETENESS: Include critical surrounding context tightly related to the facts (e.g., identifying the computation heads like 'income under the head property', relevant Acts, or Sections).
3. FAITHFULNESS: Stay strictly faithful to the source text. Use exact phrasing where possible to prevent any soft hallucination or paraphrase drift.
4. IF UNKNOWN: If the provided context does not contain the answer, say so gracefully without hallucinating."""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{question}"),
    ("system", "Relevant documents:\n{context}")
])
chain: Runnable = prompt | groq_model

from src.rag_1.rag_search import perform_vector_search

chat_history = []
log_dir = os.path.join(base_dir, "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"chat_{datetime.now():%Y%m%d_%H%M%S}.txt")

def retrieve_docs(query: str, case_id: str = None):
    return perform_vector_search(query, k=4, case_id=case_id)

def get_context(docs):
    return "\n\n".join(d.page_content for d in docs)

def log_chat(user_input: str, ai_response: str):
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n👤 USER: {user_input}\n")
        f.write(f"🤖 AI  : {ai_response}\n")

def rag_pipeline(query: str, case_id: str = None):
    docs    = retrieve_docs(query, case_id)
    context = get_context(docs)

    chat_history.append(HumanMessage(content=query))
    result = chain.invoke({
        "chat_history": chat_history,
        "question": query,
        "context": context
    })
    ai_output = result.content

    chat_history.append(AIMessage(content=ai_output))
    chat_history[:] = chat_history[-10:]

    log_chat(query, ai_output)
    return ai_output, docs

if __name__ == "__main__":
    print("📜 Legal RAG Assistant\nType 'exit' to quit.\n")
    while True:
        query = input("❓ Ask your legal question: ").strip()
        if query.lower() in {"exit", "quit"}:
            print("👋 Exiting. Take care!")
            break
        elif query:
            answer, sources = rag_pipeline(query)
            print("\n🤖 AI ANSWER:")
            print(answer)
            print("\n📚 SOURCES USED:")
            for i, d in enumerate(sources, 1):
                score = d.metadata.get("score", 0)
                print(f"  {i}. [Score: {score:.4f}] {d.page_content[:150]}...")
            print()
