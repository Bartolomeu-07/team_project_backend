from rest_framework import viewsets
from .models import Match
from .serializers import MatchSerializer

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer