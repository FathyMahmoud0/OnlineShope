
import os
import shutil
from django.conf import settings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from .models import Product
from langchain_huggingface import HuggingFaceEndpointEmbeddings

class AISearchEngine:
    def __init__(self):
        api_key = os.environ.get("HUGGINGFACEHUB_API_TOKEN")
        
        self.embeddings = HuggingFaceEndpointEmbeddings(
            huggingfacehub_api_token=api_key,
            model="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.index_path = os.path.join(settings.BASE_DIR, "faiss_index")

    def build_index(self):
        products = Product.objects.filter(is_active=True)
        documents = []

        for product in products:
            if product.text_for_embedding:
                doc = Document(
                    page_content=product.text_for_embedding,
                    metadata={"product_id": product.id}
                )
                documents.append(doc)

        if documents:
            if os.path.exists(self.index_path):
                shutil.rmtree(self.index_path)

            vector_store = FAISS.from_documents(documents, self.embeddings)
            vector_store.save_local(self.index_path)

    def search(self, query, k=5):
        if not os.path.exists(self.index_path):
            self.build_index()

        try:
            if not os.path.exists(self.index_path):
                return []

            vector_store = FAISS.load_local(
                self.index_path, 
                self.embeddings, 
                allow_dangerous_deserialization=True
            )
            
            results_with_scores = vector_store.similarity_search_with_score(query, k=k)
            
            filtered_ids = []
            for doc, score in results_with_scores:
                if score < 1.4: 
                    filtered_ids.append(doc.metadata['product_id'])

            return filtered_ids
            
        except Exception:
            return []