import joblib
import pandas as pd
from django.db.models import Q
from sklearn.linear_model import LogisticRegression

from .models import Match



# Data fetching
data = {
    # features
    'home_avg_goals_scored': [],
    'home_avg_goals_conceded': [],
    'home_avg_points': [],
    'away_avg_goals_scored': [],
    'away_avg_goals_conceded': [],
    'away_avg_points': [],
    # labels
    'home_win': [],
    'away_win': [],
}

all_matches = Match.objects.all()
train_matches = all_matches.order_by('-date_and_time')[:100]

# Calculate features and labels for every single match from training set
for match in train_matches:
    home_team = match.home_team
    away_team = match.away_team
    date = match.date_and_time

    # Loading last 10 matches data for each team
    home_team_last_ten_matches = all_matches.filter(
        (Q(home_team=home_team) | Q(away_team=home_team))
        & Q(status='Match Finished') & Q(date_and_time__lt=date)
    ).order_by('-date_and_time')[:10]
    away_team_last_ten_matches = all_matches.filter(
        (Q(home_team=away_team) | Q(away_team=away_team))
        & Q(status='Match Finished') & Q(date_and_time__lt=date)
    ).order_by('-date_and_time')[:10]

    # Skip a match if is not any history data
    if len(home_team_last_ten_matches) == 0 or len(away_team_last_ten_matches) == 0:
        continue

    # Calculate goals AVGs
    home_team_goals_scored = 0
    home_team_goals_conceded = 0
    away_team_goals_scored = 0
    away_team_goals_conceded = 0

    for m in home_team_last_ten_matches:
        if m.home_team == home_team:
            home_team_goals_scored += m.home_score
            home_team_goals_conceded += m.away_score
        else:
            home_team_goals_scored += m.away_score
            home_team_goals_conceded += m.home_score
    home_team_goals_scored_avg = home_team_goals_scored / len(home_team_last_ten_matches)
    home_team_goals_conceded_avg = home_team_goals_conceded / len(home_team_last_ten_matches)

    for m in away_team_last_ten_matches:
        if m.home_team == away_team:
            away_team_goals_scored += m.home_score
            away_team_goals_conceded += m.away_score
        else:
            away_team_goals_scored += m.away_score
            away_team_goals_conceded += m.home_score
    away_team_goals_scored_avg = away_team_goals_scored / len(away_team_last_ten_matches)
    away_team_goals_conceded_avg = away_team_goals_conceded / len(away_team_last_ten_matches)

    # Calculate points AVGs
    home_team_points = 0
    for m in home_team_last_ten_matches:
        if m.home_team == home_team:
            if m.home_score > m.away_score:
                home_team_points += 3
            elif m.home_score == m.away_score:
                home_team_points += 1
        else:
            if m.home_score < m.away_score:
                home_team_points += 3
            elif m.home_score == m.away_score:
                home_team_points += 1
    home_team_points_avg = home_team_points / len(home_team_last_ten_matches)

    away_team_points = 0
    for m in away_team_last_ten_matches:
        if m.home_team == away_team:
            if m.home_score > m.away_score:
                away_team_points += 3
            elif m.home_score == m.away_score:
                away_team_points += 1
        else:
            if m.home_score < m.away_score:
                away_team_points += 3
            elif m.home_score == m.away_score:
                away_team_points += 1
    away_team_points_avg = away_team_points / len(away_team_last_ten_matches)

    # Append data to data-features
    data['home_avg_goals_scored'].append(home_team_goals_scored_avg)
    data['away_avg_goals_scored'].append(away_team_goals_scored_avg)
    data['home_avg_goals_conceded'].append(home_team_goals_conceded_avg)
    data['away_avg_goals_conceded'].append(away_team_goals_conceded_avg)
    data['home_avg_points'].append(home_team_points_avg)
    data['away_avg_points'].append(away_team_points_avg)
    data['home_win'].append(match.home_score > match.away_score)
    data['away_win'].append(match.away_score > match.home_score)


# Create DataFrame
df = pd.DataFrame(data)

# DataFrame features
features = [
    'home_avg_goals_scored',
    'home_avg_goals_conceded',
    'home_avg_points',
    'away_avg_goals_scored',
    'away_avg_goals_conceded',
    'away_avg_points'
]

# Input data
X = df[features].values

# Labels
y_home = df['home_win'].values
y_away = df['away_win'].values

# Regression model for home team
model_home = LogisticRegression()
model_home.fit(X, y_home)
pred_home_win = model_home.predict_proba(X)[:, 1]

# -||- away team
model_away = LogisticRegression()
model_away.fit(X, y_away)
pred_away_win = model_away.predict_proba(X)[:, 1]

print("Prawdopodobieństwo zwycięstwa gospodarzy:", pred_home_win)
print("Prawdopodobieństwo zwycięstwa gości:", pred_away_win)


# Saving models to pickle files
model_home = joblib.load('model_home.pkl')
model_away = joblib.load('model_away.pkl')