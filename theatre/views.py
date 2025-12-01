from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from .forms import RegisterForm
from .models import Play, Performance, Reservation, Ticket
from .serializers import PlaySerializer, PerformanceSerializer, ReservationSerializer, TicketSerializer


class PlayViewSet(viewsets.ModelViewSet):
    queryset = Play.objects.all()
    serializer_class = PlaySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = {
        'genres__id': ['exact', 'in'],
        'genres__name': ['exact', 'in'],
        'title': ['exact', 'icontains'],
    }
    search_fields = ['title', 'genres__name']
    ordering_fields = ['title', 'id']
    ordering = ['title']

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return []


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.select_related('play', 'theatre_hall').all()
    serializer_class = PerformanceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = {
        'play__title': ['exact', 'icontains'],
        'theatre_hall__name': ['exact', 'icontains'],
        'show_time': ['exact', 'gte', 'lte'],
    }
    search_fields = ['play__title', 'theatre_hall__name']
    ordering_fields = ['show_time']
    ordering = ['show_time']

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return []

    @action(detail=True, methods=['get'])
    def free_seats_count(self, request, pk=None):
        performance = self.get_object()
        hall = performance.theatre_hall

        total_seats = hall.rows * hall.seats_in_row
        taken_count = Ticket.objects.filter(performance=performance).count()
        free_count = total_seats - taken_count

        return Response({
            "performance": performance.id,
            "hall": hall.name,
            "total_seats": total_seats,
            "taken_seats": taken_count,
            "free_seats": free_count
        })


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Ticket.objects.filter(reservation__user=self.request.user)

    def create(self, request, *args, **kwargs):
        performance_id = request.data.get("performance")
        row = int(request.data.get("row"))
        seat = int(request.data.get("seat"))

        if Ticket.objects.filter(performance_id=performance_id, row=row, seat=seat).exists():
            return Response(
                {"error": "Це місце вже заброньоване."},
                status=status.HTTP_400_BAD_REQUEST
            )

        performance = get_object_or_404(Performance, id=performance_id)
        hall = performance.theatre_hall

        if row < 1 or row > hall.rows or seat < 1 or seat > hall.seats_in_row:
            return Response(
                {"error": "Такого місця немає в цьому залі."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().create(request, *args, **kwargs)


def home(request):
    return render(request, "home.html")


def plays_list(request):
    plays = Play.objects.all()
    return render(request, "plays_list.html", {"plays": plays})


def performances_list(request):
    performances = Performance.objects.select_related("play", "theatre_hall")
    return render(request, "performances_list.html", {"performances": performances})


def reservation_form(request):
    performances = Performance.objects.select_related("play", "theatre_hall")
    return render(request, "reservation_form.html", {"performances": performances})


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})


@login_required
def make_reservation(request):
    performances = Performance.objects.select_related("play", "theatre_hall")

    if request.method == "POST":
        performance_id = request.POST.get("performance")
        row = int(request.POST.get("row"))
        seat = int(request.POST.get("seat"))

        performance = get_object_or_404(Performance, id=performance_id)
        hall = performance.theatre_hall

        if Ticket.objects.filter(performance=performance, row=row, seat=seat).exists():
            return render(request, "reservation_form.html", {
                "performances": performances,
                "error": "Це місце вже заброньоване."
            })

        if row < 1 or row > hall.rows or seat < 1 or seat > hall.seats_in_row:
            return render(request, "reservation_form.html", {
                "performances": performances,
                "error": "Такого місця немає в цьому залі."
            })

        reservation = Reservation.objects.create(user=request.user)
        Ticket.objects.create(
            reservation=reservation,
            performance=performance,
            row=row,
            seat=seat
        )

        return render(request, "reservation_form.html", {
            "performances": performances,
            "success": "Ваш квиток успішно заброньовано!"
        })

    return render(request, "reservation_form.html", {"performances": performances})



@login_required
def my_reservations(request):
    reservations = Reservation.objects.filter(user=request.user).prefetch_related(
        "tickets__performance__play",
        "tickets__performance__theatre_hall"
    )
    return render(request, "my_reservations.html", {"reservations": reservations})
