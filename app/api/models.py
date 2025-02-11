from django.db import models

class Match(models.Model):
    home_team = models.CharField(max_length=100)
    away_team = models.CharField(max_length=100)
    home_score = models.IntegerField
    away_score = models.IntegerField
    date_and_time = models.DateTimeField

    def __str__(self):
        return {
                'home_team': self.home_team,
                'away_team': self.away_team,
                'home_score': self.home_score,
                'away_score': self.away_score,
                'date_time': self.date_and_time
                }
