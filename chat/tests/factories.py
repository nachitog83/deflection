import factory

from ..models import Room


class RoomFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Room

    name = "test_room"
    slug = "test_room"
