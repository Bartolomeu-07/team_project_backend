from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from django.db.models import Q
from django.db.models.functions import Greatest
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from itertools import groupby
from collections import defaultdict
from rest_framework.viewsets import ViewSet

from .models import Match, Competition, Country, Team, Stadium
from .serializers import (MatchSerializer,
                          CompetitionSerializer,
                          CountrySerializer,
                          TeamSerializer,
                          StadiumSerializer)


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
                              type=openapi.TYPE_STRING),
            openapi.Parameter('date', openapi.IN_QUERY, description="Filter by date (DD.MM.YYYY)",
                              type=openapi.TYPE_STRING),
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
        date = self.request.query_params.get('date')

        if competition:
            queryset = queryset.filter(competition_id=competition)
        if team:
            queryset = queryset.filter(Q(home_team_id=team) | Q(away_team_id=team))
        if country_name:
            queryset = queryset.filter(competition__country__name=country_name)
        elif country_id:
            queryset = queryset.filter(competition__country_id=country_id)
        if date:
            year = date[6:10]
            month = date[3:5]
            day = date[:2]
            queryset = queryset.filter(Q(date_and_time__year=year)
                                       & Q(date_and_time__month=month)
                                       & Q(date_and_time__day=day))

        return queryset


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TeamSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="Filter by team ID",
                              type=openapi.TYPE_INTEGER)])

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Team.objects.all()
        id = self.request.query_params.get('id')

        if id:
            queryset = queryset.filter(team_id=id)

        return queryset

class LeagueViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CompetitionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Competition.objects.select_related('country').all()
        country = self.request.query_params.get('country')
        if country:
            queryset = queryset.filter(country_id=country)
        return queryset

    def list(self, request, *args, **kwargs):
        country_param = request.query_params.get('country')
        queryset = self.get_queryset()
        grouped = defaultdict(lambda: {"country_flag": None, "leagues": []})

        if country_param:
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)

        for competition in queryset:
            country = competition.country
            country_name = country.name if country else "Other"
            country_flag = country.flag if (country
                and hasattr(country, 'flag')) else \
                "https://cdn.pixabay.com/photo/2016/06/14/20/38/planet-earth-1457453_960_720.png"

            serialized = self.get_serializer(competition).data

            grouped[country_name]["country_flag"] = country_flag
            grouped[country_name]["leagues"].append(serialized)

        return Response(grouped)


class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [AllowAny]


class StadiumViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Stadium.objects.all()
    serializer_class = StadiumSerializer
    permission_classes = [AllowAny]


class RecommendedViewSet(ViewSet):

    def list(self, request, *args, **kwargs):
        top_five_matches = Match.objects.annotate(
            max_probability=Greatest('home_wins_probability', 'away_wins_probability')
            ).order_by('-max_probability')[:5]

        response_data = []
        for match in top_five_matches:
            bet = 'home' if match.home_wins_probability >= match.away_wins_probability else 'away'
            serialized_match = MatchSerializer(match).data

            response_data.append({
                'match': serialized_match,
                'bet': bet,
            })

        return Response(response_data)


class SearchViewSet(ViewSet):

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('query', openapi.IN_QUERY, description="Search by string",
                              type=openapi.TYPE_STRING)])

    def list(self, request, *args, **kwargs):
        query = request.query_params.get('query', '')

        teams = Team.objects.filter(name__icontains=query).order_by('name')
        serialized = TeamSerializer(teams, many=True)

        return Response(serialized.data)

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
