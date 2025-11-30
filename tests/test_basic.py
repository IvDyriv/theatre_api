import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from theatre.models import Play, TheatreHall, Performance, Reservation, Ticket, Genre, Actor
from django.utils import timezone


@pytest.mark.django_db
def test_create_play_with_genre_and_actor():
    genre = Genre.objects.create(name="Tragedy")
    actor = Actor.objects.create(first_name="William", last_name="Shakespeare")
    play = Play.objects.create(title="Hamlet", description="Shakespeare tragedy")
    play.genres.add(genre)
    play.actors.add(actor)

    assert play.title == "Hamlet"
    assert play.genres.first().name == "Tragedy"
    assert play.actors.first().last_name == "Shakespeare"


@pytest.mark.django_db
def test_theatre_hall_creation():
    hall = TheatreHall.objects.create(name="Main Hall", rows=5, seats_in_row=10)
    assert hall.rows == 5
    assert hall.seats_in_row == 10
    assert hall.name == "Main Hall"


@pytest.mark.django_db
def test_performance_linked_to_play_and_hall():
    play = Play.objects.create(title="Hamlet", description="Shakespeare tragedy")
    hall = TheatreHall.objects.create(name="Main Hall", rows=5, seats_in_row=10)
    perf = Performance.objects.create(play=play, theatre_hall=hall, show_time=timezone.now())

    assert perf.play.title == "Hamlet"
    assert perf.theatre_hall.name == "Main Hall"


@pytest.mark.django_db
def test_reservation_and_ticket_creation():
    user = User.objects.create_user(username="pavlo", password="test123")
    play = Play.objects.create(title="Hamlet", description="Shakespeare tragedy")
    hall = TheatreHall.objects.create(name="Main Hall", rows=5, seats_in_row=10)
    perf = Performance.objects.create(play=play, theatre_hall=hall, show_time=timezone.now())

    reservation = Reservation.objects.create(user=user)
    ticket = Ticket.objects.create(reservation=reservation, performance=perf, row=1, seat=5)

    assert ticket.row == 1
    assert ticket.seat == 5
    assert ticket.performance.play.title == "Hamlet"
    assert reservation.tickets.count() == 1


@pytest.mark.django_db
def test_login_url(client):
    url = reverse("login")
    response = client.get(url)
    assert response.status_code == 200
