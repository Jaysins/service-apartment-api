from .base import *
from src.resources.apartment import *
from src.services.apartment import *

option = OptionResource.initiate(serializers=core_serializers, service_klass=OptionService)
feature = FeatureResource.initiate(serializers=core_serializers, service_klass=FeatureService)
apartment = ApartmentResource.initiate(serializers=ApartmentResource.serializers, service_klass=ApartmentService)
available_apartment = AvailableApartmentResource.initiate(serializers=AvailableApartmentResource.serializers,
                                                          service_klass=AvailableApartmentService)

# ==============================================admin routes===========================================================

add_resource(apartment, '/apartments', '/apartments/<string:obj_id>',
             '/apartments/<string:obj_id>/<string:resource_name>')
add_resource(option, '/options', '/options/<string:obj_id>')
add_resource(feature, '/features', '/features/<string:obj_id>')
