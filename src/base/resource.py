import json

from flask_restful import Resource
from flask import request, make_response, abort
from marshmallow import EXCLUDE, ValidationError
from flask import make_response


class BaseResource(Resource):

    def __init__(self):
        """

        """

    def query(self):
        """this is the query that to the database"""
        return self.service_klass.objects

    def limit_query(self, query, req, user_context=None):
        """limit the results of a query to what want the user to see"""
        user_context = user_context

        raw_query = {"deleted": False}
        if not user_context:
            return query.raw(raw_query)
        user_id = user_context.get("id")
        raw_query.update({"user_id": user_id})
        return query.raw(raw_query)

    def limit_get(self, obj, req, user_context=None):
        """

        :param obj:
        :type obj:
        :param req:
        :type req:
        :param user_context:
        :type user_context:
        :return:
        :rtype:
        """
        model_owner_id = getattr(obj, "user_id", None)
        model_owner_pk = getattr(obj, "pk", None)
        user_id = user_context.get("id")
        if (model_owner_id and str(model_owner_id) == user_id) or (model_owner_pk and str(model_owner_pk) == user_id):
            return obj
        return abort(401, {"desc": "unauthorized"})

    def fetch(self, obj_id, req, user_context=None):
        """

        :param obj_id:
        :type obj_id:
        :param req:
        :type req:
        :param user_context:
        :type user_context:
        :return:
        :rtype:
        """
        try:
            obj = self.service_klass.get(obj_id)
        except Exception as e:
            print(e)
            return abort(404, {"desc": "requested object does not exist"})
        return obj

    def save(self, data, req, user_context=None):
        """

        """
        return self.service_klass.create(**data)

    def update(self, obj_id, data, req, user_context=None):
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
        return self.service_klass.update(obj_id, **data)

    def get(self, obj_id=None, resource_name=None):
        """

        :return:
        :rtype:
        """

        response = make_response()
        response.status_code = "200"
        response.obj_id = obj_id
        response.mimetype = "application/json"

        user_context = request.context.get("user_context")

        if not obj_id:
            base_query = self.query()
            response.context = {"results": self.limit_query(base_query, req=request, user_context=user_context)}
            return response
        obj = self.fetch(obj_id, req=request, user_context=user_context)
        if not obj:
            abort(409, {"desc": "requested resource doesn't exist"})
        response.context = {"results": self.limit_get(obj, req=request, user_context=user_context)}

        return response

    def post(self, obj_id=None, resource_name=None):
        """

        :param obj_id:
        :type obj_id:
        :param resource_name:
        :type resource_name:
        :return:
        :rtype:
        """
        response = make_response()
        response.status_code = "201"
        response.mimetype = "application/json"
        data = request.context.get("validated_data")
        user_context = request.context.get("user_context")
        print(obj_id, resource_name)
        if not obj_id and not resource_name:
            response.context = {"results": self.save(data=data, user_context=user_context, req=request)}

            return response

        if obj_id and not resource_name:
            """This is primarily for doing a update on an object"""
            obj = self.limit_get(obj=self.fetch(obj_id, user_context=user_context, req=request), req=request,
                                 user_context=user_context)
            response.context = {"results": self.update(str(obj.pk), data, req=request, user_context=user_context)}

        if obj_id and resource_name:
            """this will handle actions that will be made available to the object"""

            method = getattr(self, resource_name)

            if not method:
                abort(409, {"desc": "the method you are trying to access does not exist on this resource"})

            self.limit_get(obj=self.fetch(obj_id, user_context=user_context, req=request), req=request,
                           user_context=user_context)

            response.context = {"results": method(obj_id, data, user_context=user_context, req=request)}
        return response

    # def put(self, obj_id=None):
    #     """
    #
    #     :param obj_id:
    #     :type obj_id:
    #     :return:
    #     :rtype:
    #     """
    #
    #     self.limit_get(self.fetch(obj_id))
    #     serializer = self.serializers.get("default")
    #
    #     try:
    #         validated_data = serializer().load(data=request.json, unknown=EXCLUDE)
    #     except ValidationError as e:
    #         return abort(409, e.messages)
    #     user_context = request.environ.get("user_context")
    #
    #     resp = self.update(obj_id=obj_id, data=validated_data, user_context=user_context)
    #     resp_serializer = self.serializers.get("response")
    #     return resp_serializer().dump(resp)
    #
    # def delete(self, obj_id=None):
    #     """
    #
    #     :param obj_id:
    #     :type obj_id:
    #     :return:
    #     :rtype:
    #     """
    #
    #     self.limit_get(self.fetch(obj_id))
    #     self.service_klass.update(obj_id, deleted=True)
    #     return {"status": "successful"}

    @classmethod
    def initiate(cls, serializers=None, service_klass=None):
        cls.serializers = serializers
        cls.service_klass = service_klass
        return cls
