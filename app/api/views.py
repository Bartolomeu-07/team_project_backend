from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from django.db.models import Q, F
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from itertools import groupby

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
            openapi.Parameter('country_name', openapi.IN_QUERY, description="Filter by country name",
                              type=openapi.TYPE_STRING),
            openapi.Parameter('country_id', openapi.IN_QUERY, description="Filter by country ID",
                              type=openapi.TYPE_INTEGER),
        ]
    )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        if not (request.query_params.get('country_name')
                or request.query_params.get('country_id')
                or request.query_params.get('team')
                or request.query_params.get('competition')):
            data.sort(key=lambda item: item.get('country') or 'Undefined')
            grouped_data = {}
            for country, group in groupby(data, key=lambda item: item.get('country') or 'Undefined'):
                grouped_data[country] = list(group)
            return Response(grouped_data)
        return Response(data)

    def get_queryset(self):
        queryset = Match.objects.select_related('competition').order_by('competition__country')
        competition = self.request.query_params.get('competition')
        team = self.request.query_params.get('team')
        country_name = self.request.query_params.get('country_name')
        country_id = self.request.query_params.get('country_id')

        if competition:
            queryset = queryset.filter(competition_id=competition)
        if team:
            queryset = queryset.filter(Q(home_team_id=team) | Q(away_team_id=team))
        if country_name:
            queryset = queryset.filter(competition__country__name=country_name)
        elif country_id:
            queryset = queryset.filter(competition__country_id=country_id)

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
