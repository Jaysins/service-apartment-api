from datetime import timedelta, datetime
import settings
from marshmallow import Schema, EXCLUDE, fields as _fields, validates, ValidationError, post_load

from src.base.utils import validate_date_string
from src.models import User


class ExcludeSchema(Schema):
    class Meta:
        unknown = EXCLUDE


class CoreSchema(ExcludeSchema):
    _id = _fields.String(required=False, allow_none=True)
    code = _fields.String(required=False, allow_none=True)
    name = _fields.String(required=False, allow_none=True)
    description = _fields.String(required=False, allow_none=True)
    value = _fields.String(required=False, allow_none=True)


class AddressResponseSchema(ExcludeSchema):
    street = _fields.String(required=True, allow_none=False)
    street_line_2 = _fields.String(required=False, allow_none=True)
    state = _fields.String(required=True, allow_none=False)
    country = _fields.String(required=True, allow_none=False)


class UserResponseSchema(ExcludeSchema):
    pk = _fields.String(required=False, allow_none=True)
    date_created = _fields.DateTime(required=False, allow_none=True)
    first_name = _fields.String(required=True, allow_none=False)
    last_name = _fields.String(required=True, allow_none=False)
    email = _fields.String(required=True, allow_none=False)


class RegistrationSchema(UserResponseSchema):
    password = _fields.String(required=True, allow_none=False)


class LoginSchema(ExcludeSchema):
    password = _fields.String(required=True, allow_none=False)
    email = _fields.String(required=True, allow_none=False)

    @validates("email")
    def validate_email(self, email):
        if not User.objects.raw({"email": email}).count():
            raise ValidationError(message="Invalid email", field_name="email")


class LoginResponseSchema(UserResponseSchema):
    auth_token = _fields.String(required=True, allow_none=False)


# noinspection PyTypeChecker
class OptionSchema(ExcludeSchema):
    code = _fields.Nested(CoreSchema, required=True, allow_none=False)
    value = _fields.String(required=True, allow_none=False)


class FeatureSchema(ExcludeSchema):
    code = _fields.String(required=True, allow_none=False)
    name = _fields.String(required=True, allow_none=False)
    description = _fields.String(required=True, allow_none=False)


# noinspection PyTypeChecker
class ApartmentSchema(ExcludeSchema):
    name = _fields.String(required=True, allow_none=False)
    description = _fields.String(required=True, allow_none=False)
    options = _fields.Nested(CoreSchema, required=True, allow_none=False, many=True)
    fee = _fields.Float(required=True, allow_none=False)
    service_fee = _fields.Float(required=False, allow_none=True)
    features = _fields.List(_fields.String(required=True, allow_none=False), required=False, allow_none=False,
                            many=True)
    negotiable = _fields.Boolean(required=False, allow_none=True)
    address = _fields.Nested(AddressResponseSchema, required=True, allow_none=False)
    images = _fields.List(_fields.String(required=True, allow_none=False), required=True, allow_none=False)


# noinspection PyTypeChecker
class ApartmentResponseSchema(ApartmentSchema):
    _id = _fields.String(required=True, allow_none=False)
    active = _fields.Boolean(required=False, allow_none=True)
    options = _fields.Nested(OptionSchema, required=True, allow_none=False, many=True)
    features = _fields.Nested(FeatureSchema, required=True, allow_none=False, many=True)
    deleted = _fields.Boolean(required=False, allow_none=True)
    created_by = _fields.Nested(UserResponseSchema, required=True, allow_none=False)
    rating = _fields.Integer(required=False, allow_none=True)
    date_created = _fields.DateTime(required=True, allow_none=False)
    last_updated = _fields.DateTime(required=True, allow_none=False)


class PersonSchema(ExcludeSchema):
    """

    """
    name = _fields.String(required=True, allow_none=False)
    first_name = _fields.String(required=True, allow_none=False)
    last_name = _fields.String(required=True, allow_none=False)
    email = _fields.String(required=True, allow_none=False)
    phone = _fields.String(required=True, allow_none=False)


class ReservationSchema(ExcludeSchema):
    guest = _fields.Nested(PersonSchema(), required=True, allow_none=False)
    check_in_date = _fields.String(required=True, allow_none=False)
    checkout_date = _fields.String(required=True, allow_none=False)
    apartment = _fields.String(required=True, allow_none=False)
    note = _fields.String(required=False, allow_none=True)


class MakeApartmentAvailableSchema(ExcludeSchema):
    check_in_date = _fields.String(required=False, allow_none=True)
    check_out_date = _fields.String(required=False, allow_none=True)
    service_days = _fields.Integer(required=False, allow_none=True)

    @post_load
    def prepare_payload(self, data, **kwargs):
        check_in_date = data.get("check_in_date")
        check_out_date = data.get("check_out_date")

        if not check_out_date and not check_in_date:
            check_in_date = datetime.now()
            check_out_date = check_in_date + timedelta(days=settings.DEFAULT_CHECKOUT_DATE)

        data.update(check_in_date=check_in_date, check_out_date=check_out_date)
        return data


class NestedApartmentSchema(ExcludeSchema):
    """

    """
    name = _fields.String(required=True, allow_none=False)
    description = _fields.String(required=True, allow_none=False)
    options = _fields.Nested(OptionSchema(), required=True, allow_none=False)
    fee = _fields.Float(required=True, allow_none=False)
    address = _fields.Nested(AddressResponseSchema(), required=True, allow_none=False)


class AvailableApartmentSchema(ExcludeSchema):

    apartment = _fields.Nested(ApartmentResponseSchema(), required=True)
    apartment_data = _fields.Nested(NestedApartmentSchema(), required=True)
    check_in_date = _fields.DateTime(required=True, allow_none=False)
    checkout_date = _fields.DateTime(required=True, allow_none=False)
    _id = _fields.String(required=False, allow_none=True)
    pk = _fields.String(required=False, allow_none=True)
    service_days = _fields.String(required=False, allow_none=True)
    date_created = _fields.DateTime(required=True, allow_none=False)
    last_updated = _fields.DateTime(required=True, allow_none=False)


class CheckAvailabilitySchema(ExcludeSchema):
    days = _fields.Integer(required=True, allow_none=False)
    apartment_id = _fields.String(required=True, allow_none=False)
    check_in_date = _fields.String(required=True, allow_none=False)

    @post_load
    def prepare_payload(self, data, **kwargs):
        """

        :param data:
        :type data:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """

        check_in_date = validate_date_string(data.get("check_in_date"))
        data["check_out_date"] = check_in_date + timedelta(days=data.get("days"))
        return data
