import string
import random
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.contrib.auth.models import (AbstractBaseUser,
                                        BaseUserManager,
                                        PermissionsMixin)


class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None, referrer=None):
        if username is None:
            raise TypeError('Users must have a username.')
        if email is None:
            raise TypeError('Users must have an email address.')
        user = self.model(username=username, email=self.normalize_email(email), referrer=referrer)
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(db_index=True, max_length=100, unique=True)
    email = models.EmailField(db_index=True, unique=True)
    password = models.CharField(max_length=50)
    referrer = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    is_active = models.BooleanField(default=True)
    USERNAME_FIELD = 'email'
    objects = UserManager()


class ReferralCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='referral_codes')
    code = models.CharField(max_length=10, unique=True)
    expiry_date = models.DateTimeField(blank=False)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_referral_code()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_referral_code():
        return "REF" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))

    def is_expired(self):
        return self.expiry_date <= timezone.now()

    def __str__(self):
        return self.code
