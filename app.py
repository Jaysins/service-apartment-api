from src.resources.auth import RegisterResource, LoginResource
from src.services.core import *
from src.resources.core import *
from src.resources.apartment import ApartmentResource
from src.services.apartment import ApartmentService
from src.services.user import UserService
from src.base.middleware import AuthMiddleware
import settings
from src import app
from src.base.utils import add_resource

app.wsgi_app = AuthMiddleware(app.wsgi_app, settings=settings,
                              ignored_endpoints=["/register", "/login", "/options", "/features",
                                                 "/apartments"])

option = OptionResource.initiate(serializers=core_serializers, service_klass=OptionService)
feature = FeatureResource.initiate(serializers=core_serializers, service_klass=FeatureService)
apartment = ApartmentResource.initiate(serializers=ApartmentResource.serializers, service_klass=ApartmentService)
register = RegisterResource.initiate(serializers=RegisterResource.serializers, service_klass=UserService)
login = LoginResource.initiate(serializers=LoginResource.serializers, service_klass=UserService)


add_resource(register, '/register')
add_resource(login, '/login')
add_resource(apartment, '/apartments', '/apartments/<string:obj_id>')
add_resource(option, '/options', '/options/<string:obj_id>')
add_resource(feature, '/features', '/features/<string:obj_id>')

if __name__ == '__main__':
    app.run(debug=True, port=3000)

