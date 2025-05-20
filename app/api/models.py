from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError

class Country(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=6, unique=True, primary_key=True)
    flag = models.URLField(max_length=200, null=True, blank=True)

class Competition(models.Model):
    competition_id = models.IntegerField(unique=True, primary_key=True)
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    logo = models.URLField(max_length=500, default='')


class Team(models.Model):
    team_id = models.IntegerField(unique=True, primary_key=True)
    code = models.CharField(max_length=6, null=True, blank=True)
    name = models.CharField(max_length=100)
    league = models.ForeignKey(Competition, on_delete=models.SET_NULL, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
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


class MatchPrediction(models.Model):
    PREDICTION_TYPE_CHOICES = [
        ('winner', 'Who will win'),
        ('both_score', 'Will both teams score'),
        ('first_score', 'Who will score first'),
        ('draw', 'Will there be a draw'),
    ]
    ANSWER_CHOICES = [
        ('1', 'Home'),
        ('2', 'Away'),
        ('yes', 'Yes'),
        ('no', 'No'),
        ('without_heads', 'Without heads'),
    ]

    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    prediction_type = models.CharField(max_length=20, choices=PREDICTION_TYPE_CHOICES)
    answer = models.CharField(max_length=20, choices=ANSWER_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Logical validation for answer depending on prediction type
        if self.prediction_type == 'winner' and self.answer not in ['1', '2']:
            raise ValidationError("Answer for 'winner' must be '1' (Home) or '2' (Away).")
        if self.prediction_type == 'both_score' and self.answer not in ['yes', 'no']:
            raise ValidationError("Answer for 'both_score' must be 'yes' or 'no'.")
        if self.prediction_type == 'draw' and self.answer not in ['yes', 'no']:
            raise ValidationError("Answer for 'draw' must be 'yes' or 'no'.")
        if self.prediction_type == 'first_score' and self.answer not in ['1', '2', 'without_heads']:
            raise ValidationError("Answer for 'first_score' must be '1', '2' or 'without_heads'.")

    def save(self, *args, **kwargs):
        # Ensure validation is performed before saving
        self.full_clean()
        super().save(*args, **kwargs)
