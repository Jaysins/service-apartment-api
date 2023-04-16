from marshmallow import Schema, EXCLUDE, fields as _fields, validates, ValidationError, post_load

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
    guest = _fields.Nested(PersonSchema(), required=True, blank=False)
    check_in_date = _fields.String(required=True, blank=False)
    checkout_date = _fields.String(required=True, blank=False)
    apartment = _fields.String(required=True, allow_none=False)
    note = _fields.String(required=False, blank=True)

