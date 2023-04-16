from ..base.service import ServiceFactory
from ..models import Apartment, Reservation, AvailableApartment

BaseApartmentService = ServiceFactory.create_service(Apartment)
BaseReservationService = ServiceFactory.create_service(Reservation)
AvailableApartmentService = ServiceFactory.create_service(AvailableApartment)


class ApartmentService(BaseApartmentService):
    """

    """
    @classmethod
    def register(cls, **kwargs):
        """

        """

        return cls.create(created_by=kwargs.pop("user_id"), **kwargs)


class ReservationService(BaseReservationService):

    @classmethod
    def register(cls, **kwargs):
        """

        """