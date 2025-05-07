import joblib
import numpy as np

from .models import Match, Team


def calculate_probabilities(home_team: Team,
                            away_team: Team,
                            home_team_last_ten_matches: list[Match],
                            away_team_last_ten_matches: list[Match]):
    # Goals AVGs
    home_team_goals_scored = 0
    home_team_goals_conceded = 0
    for match in home_team_last_ten_matches:
        if match.home_team == home_team:
            home_team_goals_scored += match.home_score
            home_team_goals_conceded += match.away_score
        else:
            home_team_goals_scored += match.away_score
            home_team_goals_conceded += match.home_score
    if len(home_team_last_ten_matches) > 0:
        home_team_goals_scored_avg = home_team_goals_scored / len(home_team_last_ten_matches)
        home_team_goals_conceded_avg = home_team_goals_conceded / len(home_team_last_ten_matches)
    else:
        return 0, 0

    away_team_goals_scored = 0
    away_team_goals_conceded = 0
    for match in away_team_last_ten_matches:
        if match.home_team == away_team:
            away_team_goals_scored += match.home_score
            away_team_goals_conceded += match.away_score
        else:
            away_team_goals_scored += match.away_score
            away_team_goals_conceded += match.home_score
    if len(away_team_last_ten_matches) > 0:
        away_team_goals_scored_avg = away_team_goals_scored / len(away_team_last_ten_matches)
        away_team_goals_conceded_avg = away_team_goals_conceded / len(away_team_last_ten_matches)
    else:
        return 0, 0

    # Points AVGs
    home_team_points = 0
    for match in home_team_last_ten_matches:
        if match.home_team == home_team:
            if match.home_score > match.away_score:
                home_team_points += 3
            elif match.home_score == match.away_score:
                home_team_points += 1
        else:
            if match.home_score < match.away_score:
                home_team_points += 3
            elif match.home_score == match.away_score:
                home_team_points += 1
    home_team_points_avg = home_team_points / len(home_team_last_ten_matches)

    away_team_points = 0
    for match in away_team_last_ten_matches:
        if match.home_team == away_team:
            if match.home_score > match.away_score:
                away_team_points += 3
            elif match.home_score == match.away_score:
                away_team_points += 1
        else:
            if match.home_score < match.away_score:
                away_team_points += 3
            elif match.home_score == match.away_score:
                away_team_points += 1
    away_team_points_avg = away_team_points / len(away_team_last_ten_matches)


    # Import AI models
    model_home = joblib.load('model_home_wins.pkl')
    model_away = joblib.load('model_away_wins.pkl')

    # Load features to array
    X = np.array([[
        home_team_goals_scored_avg,
        home_team_goals_conceded_avg,
        home_team_points_avg,
        away_team_goals_scored_avg,
        away_team_goals_conceded_avg,
        away_team_points_avg
    ]])

    home_win_probability = model_home.predict_proba(X)[0][1]
    away_win_probability = model_away.predict_proba(X)[0][1]
    home_win_course = round(1 / home_win_probability, 2)
    away_win_course = round(1 / away_win_probability, 2)

    return home_win_course, away_win_course