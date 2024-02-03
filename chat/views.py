import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Message, Room

logger = logging.getLogger("chat")

# Create your views here


@login_required
def rooms(request):
    rooms = Room.objects.all()

    return render(request, "chat/rooms.html", {"rooms": rooms})


@login_required
def room(request, slug):
    room = Room.objects.get(slug=slug)
    messages = Message.objects.filter(room=room)[0:25]
    logger.info(f"User {request.user} has logged to room {slug}")

    return render(request, "chat/room.html", {"room": room, "messages": messages})
