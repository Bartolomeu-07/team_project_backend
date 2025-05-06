from rest_framework import serializers
from .models import Match, Competition, Country, Team, MatchPrediction


class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = '__all__'


class MatchSerializer(serializers.ModelSerializer):
    competition = CompetitionSerializer(read_only=True)

    class Meta:
        model = Match
        fields = '__all__'


    def to_representation(self, instance):
        return {
            "competition": instance.competition.name if instance.competition else None,
            "competition_logo": instance.competition.logo if instance.competition else None,
            "country": instance.competition.country.name if instance.competition and instance.competition.country else None,
            "country_flag": instance.competition.country.flag if instance.competition and instance.competition.country else None,
            "match_info": {
                "match_id": instance.match_id,
                "home_team": instance.home_team.name,
                "away_team": instance.away_team.name,
                "home_team_logo": instance.home_team.logo,
                "away_team_logo": instance.away_team.logo,
                "home_team_last_five_results": instance.home_team_last_five_results,
                "away_team_last_five_results": instance.away_team_last_five_results,
                "home_wins_probability": instance.home_wins_probability,
                "away_wins_probability": instance.away_wins_probability,
                "home_score": instance.home_score,
                "away_score": instance.away_score,
                "date_time": instance.date_and_time,
                "status": instance.status,
            },
        }


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'




class MatchPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchPrediction
        fields = "__all__"

    def validate(self, data):
        match = data['match']
        if not Match.objects.filter(pk=match.pk).exists():
            raise serializers.ValidationError("Invalid match ID.")
        return data
