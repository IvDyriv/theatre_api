from django.contrib import admin
from django.urls import path, include
from theatre import views
from django.contrib.auth import views as auth_views
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = routers.DefaultRouter()
router.register(r'plays', views.PlayViewSet)
router.register(r'performances', views.PerformanceViewSet)
router.register(r'reservations', views.ReservationViewSet)
router.register(r'tickets', views.TicketViewSet)

urlpatterns = [
    path('', views.home, name="home"),

    path('make-reservation/', views.make_reservation, name="make_reservation"),


    path('api/', include(router.urls)),

    path('api/auth/', include('rest_framework.urls')),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('plays/', views.plays_list, name="plays_list"),
    path('performances/', views.performances_list, name="performances_list"),
    path('reservation/', views.reservation_form, name="reservation_form"),

    path('login/', auth_views.LoginView.as_view(
        template_name="login.html",
        redirect_authenticated_user=True
    ), name="login"),
    path('logout/', auth_views.LogoutView.as_view(template_name="logout.html"), name="logout"),


    path('register/', views.register, name="register"),

    path('my-reservations/', views.my_reservations, name="my_reservations"),

    path('admin/', admin.site.urls),
]
