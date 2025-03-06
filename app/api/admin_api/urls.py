from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ..views import AdminLeagueViewSet, AdminMatchViewSet

# ADMIN API ROUTER
admin_router = DefaultRouter()
admin_router.register(r'matches', AdminMatchViewSet, basename='admin-matches')
admin_router.register(r'leagues', AdminLeagueViewSet, basename='admin-leagues')

urlpatterns = [
    path('', include(admin_router.urls)),
]