from bson import ObjectId

from src.base.resource import BaseResource
from src.schema import *


class ApartmentResource(BaseResource):
    """

    """

    serializers = {
        "default": ApartmentSchema,
        "response": ApartmentResponseSchema
    }

    def query(self):
        """

        :return:
        :rtype:
        """
        return self.service_klass.objects.raw({"deleted": False})

    def fetch(self, obj_id):
        """

        :param obj_id:
        :type obj_id:
        :return:
        :rtype:
        """
        obj = self.service_klass.find_one({"_id": ObjectId(obj_id), "deleted": False})
        return obj

    # :TODO take out save
    def save(self, data, user_context=None):
        """

        :param data:
        :type data:
        :param user_context:
        :type user_context:
        :return:
        :rtype:
        """
        if user_context:
            data["user_id"] = user_context.get("id")
        return self.service_klass.register(**data)


class AdminApartmentResource(ApartmentResource):
    serializers = {
        "default": ApartmentSchema,
        "response": ApartmentResponseSchema
    }

    def save(self, data, user_context=None):
        """

        :param data:
        :type data:
        :param user_context:
        :type user_context:
        :return:
        :rtype:
        """
        data["user_id"] = user_context.get("id")
        return self.service_klass.register(**data)
