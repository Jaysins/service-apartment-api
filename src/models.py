"""
models.py

Data model file for application. This will connect to the mongo database and provide a source for storage
for the application service

"""
from bson import SON
from pymodm.context_managers import no_auto_dereference

import settings
import pymongo

from pymongo.write_concern import WriteConcern
from pymongo.operations import IndexModel
from pymodm import connect, fields, MongoModel, EmbeddedMongoModel
from datetime import datetime, timedelta
from pymodm.common import _import as common_import
import bcrypt
import json
import jwt
from pprint import pprint

# Must always be run before any other database calls can follow
connect(settings.MONGO_DB_URI, connect=False, maxPoolSize=None)
print(settings.MONGO_DB_URI)


class ReferenceField(fields.ReferenceField):
    """
    ReferenceField
    """

    def dereference_if_needed(self, value):
        """

        :param value:
        :type value:
        :return:
        :rtype:
        """

        if isinstance(value, self.related_model):
            return value
        if self.model._mongometa._auto_dereference:
            dereference_id = common_import('pymodm.dereference.dereference_id')
            return dereference_id(self.related_model, value)
        value_stick = self.related_model._mongometa.pk.to_python(value)
        if not isinstance(value_stick, self.related_model):
            # print(type(value_stick))
            # value_stick = value_stick if value_stick and len(value_stick) > 10 else ObjectId(value_stick)
            check = self.related_model.objects.raw({"_id": value_stick})
            # print(check.count(), "dondnoenxe")
            if check.count() < 1:
                return self.related_model._mongometa.pk.to_python(value)
            return check.first()
        return self.related_model._mongometa.pk.to_python(value)


class AppMixin:
    """ App mixin will hold special methods and field parameters to map to all model classes"""

    def to_custom_son(self, exclude=None):
        """Get this Model back as a :class:`~bson.son.SON` object.

        :returns: SON representing this object as a MongoDB document.

        """
        son = SON()
        exclude = exclude if exclude else []
        with no_auto_dereference(self):
            for field in self._mongometa.get_fields():
                if field.is_undefined(self):
                    continue
                if exclude and field.attname in exclude:
                    continue
                value = self._data.get_python_value(field.attname, field.to_python)
                if field.is_blank(value):
                    son[field.mongo_name] = value
                else:
                    value = field.to_mongo(value)
                    if type(value) is list:
                        for i in value:
                            if isinstance(i, SON):
                                i.pop("_cls", None)
                                for ex in exclude:
                                    i.pop(ex, None)
                    if isinstance(value, SON):
                        value.pop("_cls", None)
                        for ex in exclude:
                            value.pop(ex, None)
                    # print(field.mongo_name)

                    # print(son[field.mongo_name])

                    son[field.mongo_name] = field.to_mongo(value)
        update_data = dict()
        if "pk" not in exclude and son.get("_id"):
            update_data.update(pk=str(son.get("_id")))
        if not son.get("code") and "code" not in exclude:
            update_data.update(code=son.get("_id"))
        son.update(**update_data)
        son.pop("_cls", None)

        return son

    def to_dict(self, exclude=None, do_dump=False):
        """

        @param exclude:
        @param do_dump:
        @return:
        """
        if isinstance(self, (MongoModel, EmbeddedMongoModel)):
            d = self.to_custom_son(exclude=exclude).to_dict()
            # [d.pop(i, None) for i in exclude]
            return json.loads(json.dumps(d, default=str)) if do_dump else d
        return self.__dict__


class User(MongoModel, AppMixin):
    """ Model for storing information about an entity or user who owns an account or set of accounts.
    _id will be equivalent to either the user_id or the entity_id
    """

    email = fields.CharField(required=False, blank=True)
    first_name = fields.CharField(required=False, blank=True)
    password = fields.CharField(required=False, blank=True)
    last_name = fields.CharField(required=False, blank=True)
    date_created = fields.DateTimeField(required=True, blank=False, default=datetime.utcnow)
    last_updated = fields.DateTimeField(required=True, blank=False, default=datetime.utcnow)

    class Meta:
        """
        Meta class
        """

        write_concern = WriteConcern(j=True)
        ignore_unknown_fields = True
        indexes = [
            IndexModel([("_cls", pymongo.DESCENDING), ("email", pymongo.ASCENDING), ("first_name", pymongo.ASCENDING),
                        ("last_name", pymongo.ASCENDING), ("date_created", pymongo.DESCENDING), ])]

    def set_password(self, password):
        """
        Password hashing logic for each model.
        This will be run on every user object when it is created.

        Arguments:
            password {str or unidecode} -- The password, in clear text, to be hashed and set on the model
        """

        if not password or not isinstance(password, (str, bytes)):
            raise ValueError("Password must be non-empty string or bytes value")

        self.password = (bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())).decode()
        # set last updated.
        self.last_updated = datetime.utcnow()

        return self.save()

    def check_password(self, password):
        """
        Password checking logic.
        This will be used whenever a user attempts to authenticate.

        Arguments:
            password {str or bytes} -- The password to be compared, in clear text.

        Raises:
            ValueError -- Raised if there is an empty value in password

        Returns:
            bool -- True if password is equal to hashed password, False if not.
        """

        if not password or not isinstance(password, (str, bytes)):
            raise ValueError("Password must be non-empty string or bytes value")

        # both password and hashed password need to be encrypted.
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

    @property
    def auth_token(self):
        """ Generate the auth token for this user from the current data embedded within the application """

        if not self.pk:
            raise ValueError("Cannot generate token for unsaved object")

        expires_in = datetime.now() + timedelta(hours=int(settings.JWT_EXPIRES_IN_HOURS))

        payload = dict(first_name=self.first_name, last_name=self.last_name, id=str(self.pk), exp=expires_in)
        # print(payload, "token the payload")
        encoded = jwt.encode(payload, key=settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded


class Address(EmbeddedMongoModel, AppMixin):
    street = fields.CharField(required=True, blank=False)
    street_line_2 = fields.CharField(required=False, blank=True)
    state = fields.CharField(required=True, blank=False)
    country = fields.CharField(required=True, blank=False)


class Status(AppMixin, MongoModel):
    code = fields.CharField(primary_key=True)
    name = fields.CharField(required=True, blank=False)


class Option(AppMixin, MongoModel):
    code = fields.CharField(primary_key=True)
    name = fields.CharField(required=True, blank=False)


class Feature(AppMixin, MongoModel):
    code = fields.CharField(primary_key=True)
    name = fields.CharField(required=True, blank=False)
    description = fields.CharField(required=True, blank=False)


class ApartmentOption(EmbeddedMongoModel):
    code = fields.ReferenceField(Option, required=True, blank=False)
    value = fields.IntegerField(required=True, blank=False)


class Apartment(MongoModel, AppMixin):
    name = fields.CharField(required=True, blank=False)
    description = fields.CharField(required=True, blank=False)
    options = fields.EmbeddedDocumentListField(ApartmentOption, required=True, blank=False)
    fee = fields.FloatField(required=True, blank=False)
    service_fee = fields.FloatField(required=False, blank=True)
    features = fields.ListField(fields.ReferenceField(Feature), required=False, blank=False)
    negotiable = fields.BooleanField(required=False, blank=True, default=False)
    active = fields.BooleanField(required=False, blank=True, default=False)
    deleted = fields.BooleanField(required=False, blank=True, default=False)
    address = fields.EmbeddedDocumentField(Address, required=True, blank=False)
    images = fields.ListField(required=True, blank=False)
    rating = fields.IntegerField(required=False, blank=True)
    created_by = fields.ReferenceField(User, required=True, blank=False)
    date_created = fields.DateTimeField(required=True, blank=False, default=datetime.utcnow)
    last_updated = fields.DateTimeField(required=True, blank=False, default=datetime.utcnow)


class Person(EmbeddedMongoModel, AppMixin):
    name = fields.CharField(required=True, blank=False)
    first_name = fields.CharField(required=True, blank=False)
    last_name = fields.CharField(required=True, blank=False)
    email = fields.CharField(required=True, blank=False)
    phone = fields.CharField(required=True, blank=False)


class Reservation(AppMixin, MongoModel):
    guest = fields.EmbeddedDocumentField(Person, required=True, blank=False)
    check_in_date = fields.DateTimeField(required=True, blank=False)
    checkout_date = fields.DateTimeField(required=True, blank=False)
    apartment = fields.ReferenceField(Apartment, required=True, blank=False)
    total_fee = fields.FloatField(required=True, blank=False)
    note = fields.CharField(required=False, blank=True)
    status = fields.ReferenceField(Status, required=True, blank=False)
    date_created = fields.DateTimeField(required=True, blank=False, default=datetime.utcnow)
    last_updated = fields.DateTimeField(required=True, blank=False, default=datetime.utcnow)


class Booking(AppMixin, MongoModel):
    status = fields.ReferenceField(Status, required=True, blank=False)
    apartment = fields.ReferenceField(Apartment, required=True, blank=False)
    number_of_guests = fields.FloatField()
    check_in_date = fields.DateTimeField(required=True, blank=False)
    checkout_date = fields.DateTimeField(required=True, blank=False)
    date_created = fields.DateTimeField(required=True, blank=False, default=datetime.utcnow)
    last_updated = fields.DateTimeField(required=True, blank=False, default=datetime.utcnow)


class EmbeddedApartment(EmbeddedMongoModel, AppMixin):
    name = fields.CharField(required=True, blank=False)
    description = fields.CharField(required=True, blank=False)
    options = fields.EmbeddedDocumentListField(ApartmentOption, required=True, blank=False)
    fee = fields.FloatField(required=True, blank=False)
    address = fields.EmbeddedDocumentField(Address, required=True, blank=False)

    class Meta:
        """
        Meta class
        """

        write_concern = WriteConcern(j=True)
        ignore_unknown_fields = True


class AvailableApartment(AppMixin, MongoModel):
    apartment = fields.ReferenceField(Apartment, required=True)
    apartment_data = fields.EmbeddedDocumentField(EmbeddedApartment, required=True)
    check_in_date = fields.DateTimeField(required=False, blank=True)
    checkout_date = fields.DateTimeField(required=False, blank=True)
    service_days = fields.IntegerField(required=False, blank=True)
    available = fields.BooleanField(required=False, blank=True)
    date_created = fields.DateTimeField(required=True, blank=False, default=datetime.utcnow)
    last_updated = fields.DateTimeField(required=True, blank=False, default=datetime.utcnow)
