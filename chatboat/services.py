import os
from huggingface_hub import InferenceClient
from products.models import Product
from products.ai import AISearchEngine

print("Loading AI Engine & Client...")
GLOBAL_ENGINE = AISearchEngine()
GLOBAL_CLIENT = InferenceClient(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    token=os.getenv("HUGGINGFACEHUB_API_TOKEN")
)
print("AI Engine Loaded!")

class ShopChatService:
    def generate_response(self, user_query):
        product_ids = GLOBAL_ENGINE.search(user_query, k=3)

        if product_ids and isinstance(product_ids[0], int):
            relevant_products = Product.objects.filter(id__in=product_ids)
        else:
            relevant_products = product_ids

        if not relevant_products:
            context_text = "No exact match found in our inventory."
        else:
            context_text = "\n".join([
                f"- Item: {p.name} | Price: {p.price} | Details: {p.description}" 
                for p in relevant_products
            ])

        system_instruction = f"""
        You are a friendly and expert sales assistant for an online shop.
        Your goal is to sell products and help customers find what they need.
        
        Here is the list of available products (Context):
        {context_text}
        
        Rules:
        1. Only recommend products from the Context above.
        2. If the user asks for something not in the list, suggest the closest alternative from the list.
        3. If the context is empty, ask the user specifically what they are looking for so you can check stock later.
        4. Mention the price in a polite way.
        5. Keep your answer short (max 3 sentences).
        """

        messages = [
            {
                "role": "system", 
                "content": system_instruction
            },
            {
                "role": "user", 
                "content": user_query
            }
        ]

        try:
            response = GLOBAL_CLIENT.chat_completion(
                messages=messages, 
                max_tokens=500,
                temperature=0.3
            )
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"API Error: {e}")
            return "Sorry, I am having trouble connecting to the server right now."
    def get_recommendations(self, current_product_name):

        search_query = f"accessories compatible with {current_product_name}"
        product_ids = GLOBAL_ENGINE.search(search_query, k=3)

        if product_ids and isinstance(product_ids[0], int):
            suggested_products = Product.objects.filter(id__in=product_ids).exclude(name=current_product_name)
        else:
            return "No specific recommendations found."

        if not suggested_products:
            return "Check out our latest collection!"

        # 2. Format the context for the LLM
        products_text = "\n".join([
            f"- {p.name} ({p.price} EGP): {p.description}" 
            for p in suggested_products
        ])

        # 3. Smart Sales Prompt
        prompt = f"""
        You are an expert shopping assistant.
        The user is currently viewing this product: "{current_product_name}".
        
        Based on that, recommend the following related items:
        {products_text}
        
        Task:
        Write a short, persuasive message (2 sentences max) explaining WHY these items go well with the {current_product_name}.
        Do not list the prices in the text, just the benefits.
        """

        messages = [
            {"role": "user", "content": prompt}
        ]

        try:
            response = GLOBAL_CLIENT.chat_completion(
                messages=messages, 
                max_tokens=200,
                temperature=0.4
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Recommendation Error: {e}")
            return "We also recommend checking out these related items."