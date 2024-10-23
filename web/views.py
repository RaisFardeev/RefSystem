from django.core.cache import cache
from rest_framework import permissions, status
from rest_framework.response import Response
from adrf.views import APIView
from asgiref.sync import sync_to_async
from web.models import User, ReferralCode
from web.serializers import UserSerializer, ReferralCodeSerializer


class RegistrationAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'status': 'created successfully'},
                status=status.HTTP_201_CREATED)
        return Response({'status': 'error', 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class CreateReferralCodeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    async def post(self, request):
        expiry_date = request.data.get('expiry_date')
        if not expiry_date:
            return Response({"detail": "Expiry date is required."}, status=status.HTTP_400_BAD_REQUEST)
        referral_code = ReferralCode(user=request.user, expiry_date=expiry_date)
        await sync_to_async(referral_code.save)()
        cache.set(f'referral_code_{request.user.email}', referral_code.code, timeout=3600)
        return Response(ReferralCodeSerializer(referral_code).data, status=status.HTTP_201_CREATED)

    async def delete(self, request):
        referral_code = await sync_to_async(ReferralCode.objects.filter)(user=request.user, is_active=True)
        if referral_code:
            referral_code.is_active = False
            await sync_to_async(referral_code.delete)()
            return Response({"detail": "Referral code deactivated successfully."}, status=status.HTTP_200_OK)
        return Response({"detail": "No active referral code found."}, status=status.HTTP_404_NOT_FOUND)


class GetReferralCodeByEmailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request,  email):
        cached_code = cache.get(f'referral_code_{email}')
        if cached_code:
            return Response({"referral_code": cached_code}, status=status.HTTP_200_OK)
        try:
            user = User.objects.get(email=email)
            referral_code = ReferralCode.objects.filter(user=user, is_active=True).first()
            if referral_code:
                cache.set(f'referral_code_{email}', referral_code.code, timeout=3600)
                return Response(ReferralCodeSerializer(referral_code).data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"detail": "No active referral code found for this user."}, status=status.HTTP_404_NOT_FOUND)


class ReferrerInfoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    async def get(self, request, referrer_id):
        try:
            referrer = await sync_to_async(User.objects.get)(id=referrer_id)
        except User.DoesNotExist:
            return Response({"detail": "Referrer not found."}, status=status.HTTP_404_NOT_FOUND)
        referrals = await sync_to_async(User.objects.filter)(referrer=referrer)
        data = await sync_to_async(UserSerializer.get_serialized_data)(referrals)
        return Response(data)
