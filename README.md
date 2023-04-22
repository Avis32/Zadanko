# About
This project is created to propose PoC solution to safely anonymize Django Models.
# How it Works
Solution implements Class that other Model Anonymizers should inherit from.
It provides methods to help with anonymization. And `anonymize()` method that handles field validation and runs all anonymization method specified in `get_anonymization_methods` <small> (/note this might be a property in the future or both :) )</small>
```rb
# zadanko/user_anonymizer/anonymizers.py
class ModelAnonymizer:
    """
    This implementation will try to make sure if all fields are taken into account when it comes to anonymizing data.
    """
```
`ModelAnonymizer` raise error when you try to anonymize model without specifing method for all fields or skipping it with class variable.
## `ModelAnonymizer` generic anonymizing methods:
* **skip(value) -> any**<br/>
    probably not even needed :) but this will skip field anonymization it's better to use `fields_to_skip`.
* **set_value(value: any) -> any**<br/>
    you have to provide value to be set in field like so:
    ```"is_active": self.set_value(False),```
* **hash_value(field) -> str** <br/>
     this hashes field values using value as a hashing key so that if value is provided it might be reversed similar to how django is hashing passwords. Already used field values might be checked for previous and hashed usage with method `encode_value` from `zadanko/user_anonymizer/utils.py` file. example can be found in here:
    ```rb
    # zadanko/user_anonymizer/models.py
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
    ```
* **delete_all_related(field) -> None** <br/> this deletes related models

example of model Anonymizer: 
```rb
# zadanko/user_anonymizer/anonymizers.py:62:
class UserAddressAnonymizer(ModelAnonymizer):
    fields_to_skip = { # this set will make `anonymize` method skip entirely anonymizing specified fields
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
```
# How to Use
If you are planning to use `ModelAnonymizer` you will probably have to extend it's implementation.
below is example of class that provided custom methods to base anonymizer.
Fields that are anonymizing Managers shouldn't return any value.
```rb
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
            UserAddressAnonymizer(instance=instance).anonymize()
```

# How to Run
## Best way to run this example is to run it with docker 
### start container
`docker build -t zadanko . && docker run --rm -d zadanko`
### access container
`docker ps` to extract container id <br>
|CONTAINER ID|IMAGE|COMMAND|CREATED|STATUS|PORTS|NAMES
|---|---|---|---|---|---|---|
|104f3eaba71c|zadanko|"python manage.py ru…"|3 seconds ago|Up 2 seconds|8000/tcp|cool_lederberg

to access shell

`docker exec -it <container_id> ./manage.py shell`

example:

`docker exec -it 104f3eaba71c ./manage.py shell`
## fun beggins 
in shell:

`from user_anonymizer.tests.factories import UserFactory, AddressFactory, ActivityLogFactory`

then create some data to test

example:
```
user = UserFactory()
AddressFactory.create_batch(10, user=user)
ActivityLogFactory.create_batch(40, user=user)
vars(user) # this is data before anonymization
user.id
Out: 1
```
run anonymizator in another terminal

`docker exec -it <container_id> ./manage.py anonymize_user 1`

get back to previous terminal and check how anonymizator worked :)

```
user.activity_logs.count() # Out: 0
user.refresh_from_db()
vars(user) # this is after anonymization
```

## Running tests
`docker exec -it <container_id> pytest`
