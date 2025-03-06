from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAdminUser
from .models import Match, Competition, Country
from .serializers import MatchSerializer, CompetitionSerializer, CountrySerializer


# USER VIEWSETS
class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = [AllowAny]


class LeagueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    permission_classes = [AllowAny]


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
