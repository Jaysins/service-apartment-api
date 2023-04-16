from bson import ObjectId

from src.base.resource import BaseResource
from src.schema import *


class ApartmentResource(BaseResource):
    """

    """

    serializers = {
        "response": ApartmentResponseSchema
    }

    def limit_get(self, obj, **kwargs):
        return obj

    def query(self):
        """

        :return:
        :rtype:
        """
        return self.service_klass.objects.raw({"deleted": False})


class AvailableApartmentResource(ApartmentResource):
    """

    """


class AdminApartmentResource(ApartmentResource):
    serializers = {
        "default": ApartmentSchema,
        "make_available": MakeApartmentAvailableSchema,
        "response": ApartmentResponseSchema
    }

    def save(self, data, req, user_context=None):
        """

        :param data:
        :type data:
        :param req:
        :type req:
        :param user_context:
        :type user_context:
        :return:
        :rtype:
        """

        data["user_id"] = user_context.get("id")
        return self.service_klass.register(**data)

    def make_available(self, obj_id, data, req, user_context):
        """

        :param obj_id:
        :type obj_id:
        :param data:
        :type data:
        :param req:
        :type req:
        :param user_context:
        :type user_context:
        :return:
        :rtype:
        """
        data["user_id"] = user_context.get("id")
        return self.service_klass.make_available(obj_id, **data)
