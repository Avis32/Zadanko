import pytest
from django.contrib.auth.models import User
from user_anonymizer.anonymizers import (ModelAnonymizer, NotAllFieldsIncluded,
                                         UserAnonymizer)
from user_anonymizer.models import ActivityLog
from user_anonymizer.tests.factories import (ActivityLogFactory,
                                             AddressFactory, UserFactory)
from user_anonymizer.utils import encode_value


def test_if_we_can_check_if_email_was_alread_used(db):
    user = UserFactory()
    user_email = user.email
    assert User.objects.filter(email=user_email).count() == 1
    UserAnonymizer(user).anonymize()
    assert User.objects.filter(email=user_email).count() == 0
    user_hashed_email = encode_value(user_email)
    assert User.objects.filter(email=user_hashed_email).count() == 1


def test_if_user_anonymizer_deletes_activity_logs(db):
    user = UserFactory()
    ActivityLogFactory.create_batch(10, user=user)
    assert user.activity_logs.count() == 10
    UserAnonymizer(user).anonymize()
    assert ActivityLog.objects.count() == 0


def test_if_user_anonymizer_keeps_addresses(db):
    user = UserFactory()
    ActivityLogFactory.create_batch(10, user=user)
    assert user.activity_logs.count() == 10
    UserAnonymizer(user).anonymize()
    assert ActivityLog.objects.count() == 0


def test_if_model_anonymizer_raises_error_when_not_all_fields_are_used(db):
    class TestUserAddressAnonymizer(ModelAnonymizer):
        fields_to_skip = {
            "id",
        }

        def get_anonymization_methods(self) -> dict[str, callable]:
            return {
                "street": self.set_value(""),
                "postal_code": self.set_value(""),
                "city": self.set_value(""),
                "contact_email": self.hash_value,
            }

    address = AddressFactory()
    with pytest.raises(NotAllFieldsIncluded):
        TestUserAddressAnonymizer(address).anonymize()

    class TestUserAddressAnonymizer(ModelAnonymizer):
        fields_to_skip = {
            "id",
            "user",
        }

        def get_anonymization_methods(self) -> dict[str, callable]:
            return {
                "postal_code": self.set_value(""),
                "city": self.set_value(""),
                "contact_email": self.hash_value,
            }

    address = AddressFactory()
    with pytest.raises(NotAllFieldsIncluded):
        TestUserAddressAnonymizer(address).anonymize()

    class TestUserAddressAnonymizer(ModelAnonymizer):
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

    address = AddressFactory()
    try:
        TestUserAddressAnonymizer(address).anonymize()
    except NotAllFieldsIncluded:
        pytest.fail(":c")
