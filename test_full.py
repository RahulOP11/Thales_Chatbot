from dotenv import load_dotenv
load_dotenv()
from src.rag.retrieval_chain import RAGChatbot

try:
    bot = RAGChatbot()
    bot.initialize()
    answer, citations, _, _, _ = bot.query(
        "What is electrostatic potential (V)?",
        grade_filter="1PUC",
        language_preference="en"
    )
    print("SUCCESS")
    print(answer)
except Exception as e:
    import traceback
    traceback.print_exc()
