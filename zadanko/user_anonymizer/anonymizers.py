from django.contrib.auth.hashers import make_password
from django.db import models
from django.db.models.manager import Manager
from user_anonymizer.utils import encode_value


class NotAllFieldsIncluded(Exception):
    pass


class ModelAnonymizer:
    """
    This implementation will try to make sure if all fields are taken into account when it comes to anonymizing data.
    This is something that will annoy developers so please dont git blame this...
    and even if so, I hope every field with my address is anonimized.
    """

    fields_to_skip: set = set()

    def __init__(self, instance: models.Model) -> None:
        self.instance = instance

    def anonymize(self):
        anonymization_methods = self.get_anonymization_methods()
        declared_fields = set(anonymization_methods.keys())
        model_fields_names = {field.name for field in self.instance._meta.get_fields()}
        missing_fields = model_fields_names - declared_fields - self.fields_to_skip
        if missing_fields:
            raise NotAllFieldsIncluded(
                f"Not All Fields included in get_anonymization_methods missing fields: {missing_fields}"
            )
        for field in declared_fields:
            instance_field = getattr(self.instance, field)
            result = anonymization_methods[field](instance_field)
            if isinstance(instance_field, Manager):
                continue
            setattr(self.instance, field, result)
        self.instance.save()

    @staticmethod
    def skip(value) -> any:
        return value

    @staticmethod
    def set_value(value: any) -> any:
        return lambda _: value

    @staticmethod
    def hash_value(field) -> str:
        if not isinstance(field, str):
            raise Exception(f"Wrong value type passed: {type(field)} expected string")
        return encode_value(value=field)

    @staticmethod
    def delete_all_related(field):
        field.all().delete()

    def get_anonymization_methods(self) -> dict[str, callable]:
        raise NotImplementedError


class UserAddressAnonymizer(ModelAnonymizer):
    fields_to_skip = {
        "id",
        "user",
    }

    def get_anonymization_methods(self) -> dict[str, callable]:
        return {
            "street": self.set_value(""),
            "postal_code": self.set_value(""),
            "city": self.set_value(""),
            "contact_email": self.hash_value,
        }


class UserAnonymizer(ModelAnonymizer):
    fields_to_skip = {
        "id",
        "last_login",
        "date_joined",
        "logentry",
    }

    def get_anonymization_methods(self) -> dict[str, callable]:
        return {
            "is_active": self.set_value(False),
            "is_staff": self.set_value(False),
            "last_name": self.set_value(""),
            "first_name": self.set_value(""),
            "is_superuser": self.set_value(False),
            "username": self.hash_value,
            "email": self.hash_value,
            "user_permissions": self.delete_all_related,
            "activity_logs": self.delete_all_related,
            "groups": self.delete_all_related,
            "password": self.make_password_unusable,
            "addresses": self.anonymize_addresses,
        }

    def make_password_unusable(self, _):
        return make_password(None)

    @staticmethod
    def anonymize_addresses(field):
        for instance in field.all():
            UserAddressAnonymizer(instance=instance).anonymize
