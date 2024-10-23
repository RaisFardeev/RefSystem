from rest_framework import serializers
from web.models import User, ReferralCode


class UserSerializer(serializers.ModelSerializer):
    referral_code = serializers.CharField(max_length=100, required=False)
    password = serializers.CharField(style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'referral_code']

    def create(self, validated_data):
        referrer = ReferralCode.objects.filter(code=validated_data.get('referral_code', None), is_active=True).first()
        if referrer:
            referrer = referrer.user
        return User.objects.create_user(username=validated_data['username'],
                                        email=validated_data['email'],
                                        password=validated_data['password'],
                                        referrer=referrer
                                        )

    @staticmethod
    def get_serialized_data(db_results):
        serializer = UserSerializer(db_results, many=True)
        return serializer.data


class ReferralCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralCode
        fields = ['id', 'code', 'expiry_date', 'is_active', 'user']
