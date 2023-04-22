import factory
from django.contrib.auth.models import User
from user_anonymizer.models import ActivityLog, Address


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: "Username %03d" % n)
    first_name = factory.Sequence(lambda n: "Agent %03d" % n)
    email = factory.Sequence(lambda n: "Email%03d@email.com" % n)
    password = factory.Sequence(lambda n: "Password%03d" % n)


class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Address

    user = factory.SubFactory(UserFactory)
    street = factory.Sequence(lambda n: "street %03d" % n)
    contact_email = factory.Sequence(lambda n: "Email%03d@email.com" % n)
    city = factory.Sequence(lambda n: "city%03d" % n)
    postal_code = factory.Sequence(lambda n: "postal_code%03d" % n)


class ActivityLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ActivityLog

    user = factory.SubFactory(UserFactory)
    activity = factory.Sequence(lambda n: "activity %03d" % n)
