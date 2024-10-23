from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from web.views import (CreateReferralCodeView,
                       ReferrerInfoView,
                       RegistrationAPIView,
                       GetReferralCodeByEmailView)


router = DefaultRouter()


schema_view = get_schema_view(
   openapi.Info(
      title="Referral System API",
      default_version='v1',
      description="API documentation for the referral system",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/registrate/', RegistrationAPIView.as_view(), name='create_referral_code'),
    path('api/referral_code/', CreateReferralCodeView.as_view(), name='create_referral_code'),
    path('api/code_by_email/<str:email>/', GetReferralCodeByEmailView.as_view(), name='create_referral_code'),
    path('api/referrals/<int:referrer_id>/', ReferrerInfoView.as_view(), name='retrieve_referrals'),
]