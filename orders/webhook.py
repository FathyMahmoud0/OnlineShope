import stripe
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .tasks import confirm_order_payment

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        order_id = payment_intent['metadata'].get('order_id')
        
        if order_id:
            confirm_order_payment.delay(order_id)

    return HttpResponse(status=200)