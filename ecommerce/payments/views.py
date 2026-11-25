import razorpay
from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from .models import Payment
from .serializers import PaymentSerializer,CreatePaymentSerializer,VerifyPaymentSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny

class PaymentView(ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get','head','options']

    def get_queryset(self):
        user=self.request.user
        return (
            Payment.objects.filter(customer=user)
        )

class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['post','head','options']

    def post(self,request):
        user=self.request.user
        serializer=CreatePaymentSerializer(data=request.data,context={"request":request})
        serializer.is_valid(raise_exception=True)
        order_id=serializer.validated_data["order_id"]
        order=user.orders.get(id=order_id)
        if order.payment_method=="COD":
            return Response(
                {
                    'message': "For cod no need of online payment"
                },
                status=status.HTTP_200_OK
            )
        client=razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,
                              settings.RAZORPAY_KEY_SECRET))
        razorpay_order= client.order.create(
            {
            "amount":int(order.total_amount*100),
            "currency": "INR",
            "receipt": order.order_number
            }
        )
        Payment.objects.create(
            customer=user,
            order=order,
            razorpay_order_id=razorpay_order["id"],
            amount=order.total_amount,
            status="PENDING"
        )
        return Response(
            {
                'razorpay_order_id':razorpay_order['id'],
                "amount":razorpay_order["amount"],
                "currency":"INR",
                "key":settings.RAZORPAY_KEY_ID
            },
            status = status.HTTP_201_CREATED
        )

class RazorPayWebhookView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    http_method_names = ["post", "head", "options"]
    def post(self,request):

        raw_body = request.body.decode("utf-8")
        signature = request.headers.get("X-Razorpay-Signature")
        if not signature:
            return Response(
                {
                    "message":"Missing signature"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            client.utility.verify_webhook_signature(
                raw_body,signature,settings.RAZORPAY_WEBHOOK_SECRET
            )
        except razorpay.errors.SignatureVerificationError:
            return Response(
                {"error": "Invalid signature"},
                status=status.HTTP_400_BAD_REQUEST
            )
        event = request.data.get("event")
        payment_entity = request.data.get("payload", {}).get("payment", {}).get("entity", {})
        razorpay_payment_id=payment_entity.get("id")
        razorpay_order_id = payment_entity.get("order_id")
        refund_payment_id = request.data.get("payload", {}).get("refund", {}).get("entity", {}).get("payment_id")
        if refund_payment_id:
            if event=='refund.processed':
               with transaction.atomic():
                 refund= Payment.objects.select_for_update().select_related("order").filter(
                       razorpay_payment_id=refund_payment_id).first()
                 if refund is not None:
                     refund.status = "REFUNDED"
                     refund.save(update_fields=["status"])
        if not razorpay_order_id:
            return Response(
                {
                    "status":"ignored"
                },
                status=status.HTTP_200_OK
            )
        with transaction.atomic():
            payment=Payment.objects.select_for_update().select_related("order"
                                                                       ).filter(razorpay_order_id=razorpay_order_id
                                                                                ).first()
            if payment is None:
                return Response(
                    {
                      "status":"Payment Not Found"
                    },
                    status=status.HTTP_200_OK
                )
            if payment.status=='SUCCESS':
                return Response(
                    {"status": "already processed"},
                    status=status.HTTP_200_OK
                )
            if event == 'payment.captured':
                payment.razorpay_payment_id = razorpay_payment_id
                payment.razorpay_signature = signature
                payment.status = "SUCCESS"
                payment.save(update_fields=["razorpay_payment_id", "razorpay_signature", "status"])
                payment.order.status = "CONFIRMED"
                payment.order.save(update_fields=["status"])
            elif event == "payment.failed":
                payment.status = "FAILED"
                payment.save(update_fields=["status"])

        return Response(
            {"message": "Done"},
                status=status.HTTP_200_OK
            )

class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        user=request.user
        serializer=VerifyPaymentSerializer(data=request.data,context={"request":request})
        serializer.is_valid(raise_exception=True)
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        razorpay_order_id = serializer.validated_data['razorpay_order_id']
        razorpay_payment_id=serializer.validated_data['razorpay_payment_id']
        razorpay_signature=serializer.validated_data['razorpay_signature']
        try:
            client.utility.verify_payment_signature({
            'razorpay_signature': razorpay_signature,
            'razorpay_order_id' : razorpay_order_id,
            'razorpay_payment_id':razorpay_payment_id
            })
        except razorpay.errors.SignatureVerificationError:
            return Response(
                {
                    "message":"Invalid Payment"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        with transaction.atomic():
            updates = Payment.objects.select_for_update().select_related("order").filter(
                customer=user,razorpay_order_id=razorpay_order_id).first()
            if updates is None:
                return Response(
                    {
                        'error': "Payment not found"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            if updates.status == "SUCCESS":
                return Response(
                    {
                        'message': "Payment Successful"
                    },
                    status=status.HTTP_200_OK
                )
            updates.status = 'SUCCESS'
            updates.razorpay_order_id = razorpay_order_id
            updates.razorpay_payment_id = razorpay_payment_id
            updates.razorpay_signature = razorpay_signature
            updates.save(update_fields=["razorpay_payment_id", "razorpay_signature", "status"])
            updates.order.status = 'CONFIRMED'
            updates.order.save(update_fields=["status"])
            return Response(
                {
                    'message': 'Payment Successful'
                },
                status=status.HTTP_200_OK
            )


