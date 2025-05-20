from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import (MatchViewSet,LeagueViewSet,
                    CountryViewSet, TeamViewSet,
                    RecommendedViewSet, SearchViewSet, MatchPredictionViewSet)

# API ROUTER
api_router = DefaultRouter()
api_router.register(r'matches', MatchViewSet, basename='matches')
api_router.register(r'competitions', LeagueViewSet, basename='competitions')
api_router.register(r'countries', CountryViewSet, basename='countries')
api_router.register(r'teams', TeamViewSet, basename='teams')
api_router.register(r'recommended', RecommendedViewSet, basename='recommended matches')
api_router.register(r'search', SearchViewSet, basename='search')
api_router.register(r'predictions', MatchPredictionViewSet, basename='predictions')

# API schema configuration for Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="Pewniaczki API",
        default_version='v1',
        description="API documentation",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('', include(api_router.urls)),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0),
            name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),
]