from ..base.service import ServiceFactory
from ..models import Apartment

BaseApartmentService = ServiceFactory.create_service(Apartment)


class ApartmentService(BaseApartmentService):
    """

    """
    @classmethod
    def register(cls, **kwargs):
        """

        """

        user_id = "6136dfa7a1ab9d318bcfcb9d"
        return cls.create(created_by=user_id, **kwargs)

