from django.db import models
from django.utils.timezone import now


class Country(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=6, unique=True, primary_key=True)
    flag = models.URLField(max_length=200, null=True, blank=True)

class Competition(models.Model):
    competition_id = models.IntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    logo = models.URLField(max_length=500, default='')


class Stadium(models.Model):
    stadium_id = models.IntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    capacity = models.IntegerField(null=True, blank=True)
    surface = models.CharField(max_length=100, null=True, blank=True)
    image = models.URLField(max_length=500, default='')


class Team(models.Model):
    team_id = models.IntegerField(unique=True, primary_key=True)
    code = models.CharField(max_length=6, null=True, blank=True)
    name = models.CharField(max_length=100)
    league = models.ForeignKey(Competition, on_delete=models.SET_NULL, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    stadium = models.ForeignKey(Stadium, on_delete=models.SET_NULL, null=True, blank=True)
    founded = models.IntegerField(null=True, blank=True)
    logo = models.URLField(max_length=500, default='')

    @property
    def last_five_matches(self):
        return Match.objects.filter(
            models.Q(home_team=self) | models.Q(away_team=self),
            status='Match Finished',
        ).order_by('-date_and_time')[:5]


class Match(models.Model):
    match_id = models.IntegerField(unique=True, primary_key=True)
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, null=True, blank=True)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, to_field='team_id', related_name='home_matches')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, to_field='team_id', related_name='away_matches')
    home_team_last_five_results = models.JSONField(null=True, blank=True)
    away_team_last_five_results = models.JSONField(null=True, blank=True)
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    home_wins_probability = models.FloatField(null=True, blank=True)
    away_wins_probability = models.FloatField(null=True, blank=True)
    date_and_time = models.DateTimeField(default=now)
    status = models.CharField(max_length=10, default='')

    class Meta:
        indexes = [
            models.Index(fields=['away_team', 'home_team']),
            models.Index(fields=['competition']),
        ]
