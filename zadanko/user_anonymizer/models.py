from django.contrib.auth.models import User
from django.db import models
from user_anonymizer.utils import encode_value


class ActivityLog(models.Model):
    user = models.ForeignKey(
        User, related_name="activity_logs", on_delete=models.CASCADE
    )
    activity = models.CharField(max_length=512)


class Address(models.Model):
    user = models.ForeignKey(User, related_name="addresses", on_delete=models.CASCADE)
    street = models.CharField(max_length=128, default="")
    postal_code = models.CharField(max_length=128, default="")
    city = models.CharField(max_length=128, default="")
    contact_email = models.EmailField(blank=True)


class AnonymizedUser(User):
    class Meta:
        proxy = True

    @staticmethod
    def was_email_anonymized(email: str) -> bool:
        hashed_email = encode_value(email)
        return User.objects.filter(email=hashed_email).exists()

    @staticmethod
    def was_username_anonymized(username: str) -> bool:
        hashed_username = encode_value(username)
        return User.objects.filter(username=hashed_username).exists()
