from dotenv import load_dotenv
load_dotenv()
from src.rag.vector_store import VectorStoreManager

vm = VectorStoreManager()
vm.load_vectorstore()
try:
    docs = vm.search('What is electrostatic potential?', k=5, filter_dict={'grade': '1PUC'})
    for doc in docs:
        print(doc.page_content)
    print("SUCCESS")
except Exception as e:
    import traceback
    traceback.print_exc()
