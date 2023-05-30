import json

from flask import abort
from pymodm import MongoModel
from pymodm.queryset import QuerySet
from werkzeug.wrappers import Request, Response
from flask_http_middleware import BaseHTTPMiddleware
import jwt
from marshmallow import EXCLUDE, ValidationError
from bson import ObjectId
from .utils import validate_date_filter


def validate(request, schema, header_data=None):
    """

    """
    req_data = request.json
    if header_data:
        for k, v in header_data.items():
            if v:
                req_data[k] = v
    print("request data===>", req_data)

    try:
        data = schema().load(data=req_data, unknown=EXCLUDE)
    except ValidationError as e:
        print("Errors", e)
        return abort(409, e.messages)
    print("validated===data===>", data)
    return data


def marshal(resp, schema, res=None, req=None):
    """
    prepares the response object with the specified schema
    :param resp: the falcon response object
    :param res: the object
    :param req: the object
    :param schema: the schema class that should be used to validate the response
    :return: falcon.Response
    """
    data = resp

    resp_ = None

    res_context = res.context if res else None
    req_context = req.context if req else None

    print(isinstance(data, MongoModel), "sssss", data, resp)
    if isinstance(data, list) or isinstance(data, QuerySet):
        print("it s me", schema)
        resp_ = schema(context=dict(res=res_context, req=req_context)).dump(list(data), many=True)
        print("after===>")
    if isinstance(data, dict):
        try:
            resp_ = schema().load(data=data, unknown=EXCLUDE)
        except ValidationError as e:
            print("Errors", e)
            return abort(409, e.messages)
    if isinstance(data, MongoModel):
        print("goooooooooo")
        data.context_ = res_context
        resp_ = schema(context=dict(res=res_context, req=req_context)).dump(data)

    print("i am resp===========>")

    return resp_


class AuthMiddleware(BaseHTTPMiddleware):
    '''
    Simple WSGI middleware
    '''

    def __init__(self, app, settings, ignored_endpoints=None):
        super().__init__()
        self.app = app
        self.ignored_endpoints = ignored_endpoints
        self.settings = settings

    def dispatch(self, request, call_next):

        resource = self.app.view_functions.get(request.endpoint)
        if not resource:
            abort(404, {"desc": "Resource does  not exist"})

        resource_class = resource.view_class

        print(resource_class)
        request.context = {}

        user_context = self.validate_token(token=request.headers.get("Authorization", None))
        print("ia m ", user_context)
        if not user_context and not self.check_ignored_endpoints(path=request.path, base_path=self.settings.API_PREFIX):
            return abort(401, {"message": "invalid token"})

        request.context.update(user_context=user_context)
        return call_next(request)

    def validate_token(self, token):
        """

        :param token:
        :type token:
        :return:
        :rtype:
        """
        try:
            token = token.split("Bearer ")[1]
            data = jwt.decode(token, self.settings.JWT_SECRET_KEY, algorithms=self.settings.JWT_ALGORITHM)
            return data
        except Exception as e:
            print(e)
        return None

    def check_ignored_endpoints(self, path, base_path=''):
        """separate possible base api endpoints """
        if base_path is None:
            base_path = ""
        if not self.ignored_endpoints:
            return

        relative_path = path.split(base_path)[-1]
        for i in self.ignored_endpoints:
            if not i.startswith("/"):
                i = "/" + i
            l = len(i)
            print(i[:], relative_path[:l])
            if i[:] == relative_path[:l]:
                return True
        return False


class RequestResponseMiddleware(BaseHTTPMiddleware):
    """

    """

    def __init__(self, app, api, settings):
        super().__init__()
        self.app = app
        self.api = api
        self.settings = settings

    def get_named_param_from_path(self, request, resource):
        """

        :param request:
        :type request:
        :param resource:
        :type resource:
        :return:
        :rtype:
        """
        base_path = self.api.url_for(resource)
        endpoint = (request.path.replace(f"{base_path}/", "")).split("/")
        if not endpoint:
            return request
        request.context.update(obj_id=endpoint[0])
        if len(endpoint) < 2:
            return request
        request.context.update(resource_name=endpoint[1])
        return request

    def dispatch(self, request, call_next):

        resource = self.app.view_functions.get(request.endpoint)

        resource_class = resource.view_class

        request = self.get_named_param_from_path(request, resource=resource_class)

        validated_data = self.process_resource(request, resource=resource_class)

        if type(validated_data) not in [dict, list]:
            return validated_data

        request.context.update(validated_data=validated_data)

        response = call_next(request)

        req_method = request.method.lower()

        if req_method == "get" and not response.obj_id:
            response = self.process_query(request, response, resource=resource_class)

        response = self.process_response(request, response, resource=resource_class)

        results = response.context.get("results")

        if type(results) not in [dict, list]:
            return results

        if req_method == "get" and not response.obj_id:
            response.data = json.dumps({"results": results, **response.context.get("resp", {})})
        else:
            response.data = json.dumps(results)
        return response

    def process_resource(self, request, resource):
        """

        """
        print(self)

        if request.method.lower() not in ["post", "put"]:
            return {}

        resource_name = request.context.get("resource_name")
        obj_id = request.context.get("obj_id")
        serializer = resource.serializers.get("default")

        if obj_id:
            serializer = resource.serializers.get(resource_name, serializer)
        if resource_name:
            serializer = resource.serializers.get(resource_name, serializer)

        print("i am serializer================>"
              "", serializer, resource_name)
        if not serializer:
            abort(404, {"desc": "cannot make request to this route"})
        return validate(request, serializer, header_data=request.headers)

    def parse_type(self, k, v, resource):
        """
        check if the value of a param is an ObjectId and apply appropriate query modification
        :param k:
        :param resource:
        :param v: the value to examine
        :return:
        """
        attr = getattr(resource.service_klass.model_class, k, None)
        if not attr:
            return v

        typ = type(attr)
        name = typ.__name__

        print(name)
        if name == "ObjectIdField" or (name == "ReferenceField" and ObjectId.is_valid(v)):
            return ObjectId(v)

        if name == "DateTimeField":
            return validate_date_filter(v)
        return v

    def process_query(self, request, response, resource):
        """

        """
        print(self)
        print(request.values.to_dict())

        params = request.values.to_dict()

        filter_by = params.get("filter_by")
        results = {}
        if filter_by:
            request.filter_by = json.loads(filter_by)
            response = self.filter_response(request, response, resource)
        query = params.get("query")
        if query:
            request.query = query
            response = self.query_response(request, response, resource)

        sort = params.get("sort")
        if sort:
            request.sort = sort
            response = self.sort_response(request, response, resource)

        response.context.update(resp=params)

        return response

    def filter_response(self, request, response, resource):
        """

        """

        filter_ = {}
        for key, value in request.filter_by.items():
            val = self.parse_type(k=key, v=value, resource=resource)
            if not val:
                continue
            filter_[key] = val

        results = response.context.get("results")
        response.context.update(results=results.raw(filter_))
        return response

    def query_response(self, request, response, resource):
        """

        """
        print(request.query)
        return response

    def sort_response(self, request, response, resource):
        """

        """
        print(request.sort)
        return response

    def process_response(self, request, response, resource):
        """

        """

        req_context = request.context

        obj_id = req_context.get("obj_id")

        resource_name = req_context.get("resource_name")

        serializer = resource.serializers.get("response")

        if obj_id:
            serializer = resource.serializers.get("%s_response" % obj_id, serializer)
        if resource_name:
            serializer = resource.serializers.get("%s_response" % resource_name, serializer)
        if not getattr(response, "context"):
            return response

        context = response.context

        context.update(results=marshal(resp=response.context.get("results"), req=request, schema=serializer,
                                       res=response))

        response.context = context

        print(response.context)
        return response
