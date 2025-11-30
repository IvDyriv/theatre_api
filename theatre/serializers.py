from rest_framework import serializers
from .models import *

class PlaySerializer(serializers.ModelSerializer):
    genres = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name"   # повертає назву жанру замість ID
    )

    class Meta:
        model = Play
        fields = ["id", "title", "description", "genres"]

class PerformanceSerializer(serializers.ModelSerializer):
    play_title = serializers.CharField(source="play.title", read_only=True)
    hall_name = serializers.CharField(source="theatre_hall.name", read_only=True)

    class Meta:
        model = Performance
        fields = ["id", "play", "play_title", "theatre_hall", "hall_name", "show_time"]

class TicketSerializer(serializers.ModelSerializer):
    play_title = serializers.CharField(source="performance.play.title", read_only=True)
    show_time = serializers.DateTimeField(source="performance.show_time", read_only=True)
    hall_name = serializers.CharField(source="performance.theatre_hall.name", read_only=True)

    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "performance", "reservation",
                  "play_title", "show_time", "hall_name"]


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Reservation
        fields = ['id', 'user', 'username', 'created_at', 'tickets']
