from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Match, Competition, Country, Team
from .serializers import (MatchSerializer,
                          CompetitionSerializer,
                          CountrySerializer,
                          TeamSerializer)


# USER VIEWSETS
class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = MatchSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('competition', openapi.IN_QUERY, description="Filter by competition ID",
                              type=openapi.TYPE_INTEGER),
            openapi.Parameter('team', openapi.IN_QUERY, description="Filter by team ID (home or away)",
                              type=openapi.TYPE_INTEGER),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Custom list to ensure Swagger shows parameters"""
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Match.objects.all()
        competition = self.request.query_params.get('competition')
        team = self.request.query_params.get('team')

        if competition:
            queryset = queryset.filter(competition_id=competition)
        if team:
            queryset = queryset.filter(Q(home_team_id=team) | Q(away_team_id=team))

        return queryset


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TeamSerializer
    permission_classes = [AllowAny]
    queryset = Team.objects.all()


class LeagueViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CompetitionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Competition.objects.all()
        country = self.request.query_params.get('country')

        if country:
            queryset = queryset.filter(country_id=country)

        return queryset


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [AllowAny]


# ADMIN VIEWSETS
# class AdminMatchViewSet(viewsets.ModelViewSet):
#     queryset = Match.objects.all()
#     serializer_class = MatchSerializer
#     permission_classes = [IsAdminUser]
#
#
# class AdminLeagueViewSet(viewsets.ModelViewSet):
#     queryset = Competition.objects.all()
#     serializer_class = CompetitionSerializer
#     permission_classes = [IsAdminUser]
