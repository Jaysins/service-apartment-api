from ..base.service import ServiceFactory
from ..models import *


OptionService = ServiceFactory.create_service(Option)
FeatureService = ServiceFactory.create_service(Feature)
