from .base import *

from src.resources.auth import RegisterResource, LoginResource
from src.services.user import UserService
from src.services.apartment import *
from src.resources.apartment import *

register = RegisterResource.initiate(serializers=RegisterResource.serializers, service_klass=UserService)
login = LoginResource.initiate(serializers=LoginResource.serializers, service_klass=UserService)
admin_apartment = AdminApartmentResource.initiate(serializers=AdminApartmentResource.serializers,
                                                  service_klass=ApartmentService)
# admin_available_apartment = AvailableApartmentResource.initiate(serializers=AvailableApartmentResource.serializers,
#                                                                 service_klass=AvailableApartmentService)

add_resource(admin_apartment, '/admin_apartments', '/admin_apartments/<string:obj_id>',
             '/admin_apartments/<string:obj_id>/<string:resource_name>')

add_resource(register, '/register')
add_resource(login, '/login')
