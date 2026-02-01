from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .services import ShopChatService
from products.models import Product

@api_view(['POST'])
def chat_bot_view(request):
    user_message = request.data.get('message')
    
    if not user_message:
        return Response({"error": "No message provided"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        service = ShopChatService()
        response_text = service.generate_response(user_message)
        return Response({"response": response_text}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(['GET'])
def smart_recommendation_view(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        
        service = ShopChatService()
        recommendation_text = service.get_recommendations(product.name)
        
        return Response({
            "product": product.name,
            "ai_suggestion": recommendation_text
        }, status=status.HTTP_200_OK)

    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)