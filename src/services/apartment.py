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

    @classmethod
    def make_available(cls, obj_id, **kwargs):
        """

        :param obj_id:
        :type obj_id:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """
        apartment = cls.get(obj_id)

        data = {"apartment": obj_id,
                "apartment_data": {
                    "name": apartment.name,
                    "description": apartment.description,
                    "options": apartment.options,
                    "fee": apartment.fee,
                    "address": apartment.address.to_dict(exclude=["code", "_id", "date_created", "last_updated"]),
                },
                **kwargs}

        apartment_data = ApartmentService.find_one({"apartment": apartment.pk})
        if apartment_data:
            AvailableApartmentService.update(apartment_data.pk, **data)
        else:
            AvailableApartmentService.create(**data)
        return apartment


class ReservationService(BaseReservationService):

    @classmethod
    def register(cls, **kwargs):
        """

        """
