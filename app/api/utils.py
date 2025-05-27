import random
import requests
import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from django.db.models import Q

from .models import Country, Competition, Match, Team, Stadium
from .logistic_regression import calculate_probabilities

API_KEY = '0707a7f0e4872c2bfc2763c2b27ba7b4'
HEADERS = {"x-apisports-key": API_KEY}
url = "https://v3.football.api-sports.io/"

def fetch_and_create_countries():
    response = requests.get(url + 'countries', headers=HEADERS)
    if response.status_code == 200:
        data = response.json().get('response', [])
        existing_codes = set(Country.objects.values_list('code', flat=True))
        new_countries = []

        for item in data:
            code = item.get('code')
            if code and code not in existing_codes:
                name = item.get('name')
                flag = item.get('flag')
                new_countries.append(Country(code=code, name=name, flag=flag))
                existing_codes.add(code)
        if new_countries:
            Country.objects.bulk_create(new_countries)
            print(f"{len(new_countries)} new countries created.")
        else:
            print("No new countries to add.")
    else:
        print("Error during fetching countries:", response.status_code)

def fetch_and_create_competitions():
    response = requests.get(url + 'leagues', headers=HEADERS)
    if response.status_code == 200:
        data = response.json().get('response', [])
        existing_competitions_ids = set(Competition.objects.values_list('competition_id', flat=True))
        countries = Country.objects.all()
        new_competitions = []

        for item in data:
            competition_data = item.get('league', {})
            competition_id = competition_data.get('id')

            if competition_id and competition_id not in existing_competitions_ids:
                country_code = item['country'].get('code')
                if country_code:
                    country = countries.get(code=country_code)
                else:
                    country = None
                name = competition_data.get('name')
                logo = competition_data.get('logo')
                new_competitions.append(Competition(competition_id=competition_id, name=name, logo=logo, country=country))
        if new_competitions:
            Competition.objects.bulk_create(new_competitions)
            print(f"{len(new_competitions)} new competitions created.")
        else:
            print("No new competitions to add.")
    else:
        print("Error during fetching competitions:", response.status_code)



def fetch_and_create_teams_and_venues():
    """
    The 'league' field is assigned based on the order in which the competitions are created.

    The data should be retrieved in the following order:
    1. National competitions
    2. International competitions
    """
    competitions_to_create = [135, 61, 78, 2, 140, 39]

    for competition_id in competitions_to_create:
        params = {
            'league': competition_id,
            'season': '2023'
        }

        response = requests.get(url + 'teams', headers=HEADERS, params=params)
        if response.status_code == 200:

            # Creating stadiums
            data = response.json().get('response', [])
            existing_stadiums_ids = set(Stadium.objects.values_list('stadium_id', flat=True))
            new_stadiums = []

            for item in data:
                stadium_data = item.get('venue', {})
                stadium_id = stadium_data.get('id')
                if stadium_data and stadium_id not in existing_stadiums_ids:
                    new_stadiums.append(Stadium(
                        stadium_id=stadium_id,
                        name=stadium_data.get('name'),
                        address = stadium_data.get('address'),
                        city = stadium_data.get('city'),
                        capacity = stadium_data.get('capacity'),
                        surface = stadium_data.get('surface'),
                        image = stadium_data.get('image')
                    ))
                existing_stadiums_ids.add(stadium_id)

            if new_stadiums:
                Stadium.objects.bulk_create(new_stadiums)
                print(f"{len(new_stadiums)} new stadiums created.")
            else:
                print(f"No new stadiums to add.")

            # Creating teams
            data = response.json().get('response', [])
            league = Competition.objects.get(competition_id=params.get('league'))
            countries = Country.objects.all()
            existing_teams_ids = set(Team.objects.values_list('team_id', flat=True))
            new_teams = []

            for item in data:
                stadium_id = item.get('venue').get('id')
                team_data = item.get('team', {})
                team_id = team_data.get('id')

                if team_id and team_id not in existing_teams_ids:
                    code = team_data.get('code')
                    name = team_data.get('name')
                    founded = team_data.get('founded')
                    country_name = team_data.get('country')
                    try:
                        country = countries.get(name=country_name)
                    except:
                        country = None
                    try:
                        stadium = Stadium.objects.get(stadium_id=stadium_id)
                    except:
                        stadium = None
                    logo = team_data.get('logo')
                    new_teams.append(Team(team_id=team_id,
                                                 code=code,
                                                 name=name,
                                                 league=league,
                                                 country=country,
                                                 stadium=stadium,
                                                 founded=founded,
                                                 logo=logo))
                    existing_teams_ids.add(team_id)
            if new_teams:
                Team.objects.bulk_create(new_teams)
                print(f"{len(new_teams)} new teams created.")
            else:
                print(f"No new teams to add.")

        else:
            print("Error during fetching teams and venues:", response.status_code)


def create_or_update_match_data():
    competitions_to_update = [135, 2, 61, 78, 140, 39]


    for competition_id in competitions_to_update:
        params = {
            'league': competition_id,
            'season': '2023',
        }

        response = requests.get(url + 'fixtures', headers=HEADERS, params=params)
        if response.status_code == 200:
            data = response.json().get('response', [])
            existing_matches = list(Match.objects.filter(competition_id=params.get('league')).order_by('-date_and_time'))
            existing_matches_ids = set(m.match_id for m in existing_matches)
            competition = Competition.objects.get(competition_id=params.get('league'))
            teams = Team.objects.all()
            new_matches = []

            for item in data:
                match_id = item.get('fixture').get('id')
                if match_id and match_id not in existing_matches_ids:
                    home_team_id = item.get('teams').get('home').get('id')
                    away_team_id = item.get('teams').get('away').get('id')
                    home_team = teams.get(team_id=home_team_id)
                    away_team = teams.get(team_id=away_team_id)
                    date = item.get('fixture').get('date')

                    # Loading last 10 matches data for each team
                    home_team_last_ten_matches = [
                        match for match in existing_matches
                        if (match.home_team == home_team or match.away_team == home_team)
                           and match.status == 'Match Finished'
                           and match.date_and_time < date
                    ]
                    home_team_last_ten_matches = sorted(home_team_last_ten_matches, key=lambda m: m.date_and_time,
                                                        reverse=True)[:10]

                    away_team_last_ten_matches = [
                        match for match in existing_matches
                        if (match.home_team == away_team or match.away_team == away_team)
                           and match.status == 'Match Finished'
                           and match.date_and_time < date
                    ]
                    away_team_last_ten_matches = sorted(away_team_last_ten_matches, key=lambda m: m.date_and_time,
                                                        reverse=True)[:10]

                    home_team_last_five_results = random.choices(['W', 'D', 'L'], k=5)
                    away_team_last_five_results = random.choices(['W', 'D', 'L'], k=5)
                    home_score = item.get('goals').get('home')
                    away_score = item.get('goals').get('away')
                    home_wins_probability, away_wins_probability = calculate_probabilities(
                        home_team, away_team, home_team_last_ten_matches, away_team_last_ten_matches
                    )
                    status = item.get('fixture').get('status').get('long')

                    new_match = Match(match_id=match_id,
                                      competition=competition,
                                      home_team=home_team,
                                      away_team=away_team,
                                      home_team_last_five_results=home_team_last_five_results,
                                      away_team_last_five_results=away_team_last_five_results,
                                      home_score=home_score,
                                      away_score=away_score,
                                      home_wins_probability=home_wins_probability,
                                      away_wins_probability=away_wins_probability,
                                      date_and_time=date,
                                      status=status
                                      )
                    new_matches.append(new_match)
                    existing_matches.append(new_match)
            if new_matches:
                Match.objects.bulk_create(new_matches)
                print(f"{len(new_matches)} new {competition.name} matches created.")
            else:
                print(f"No new {competition.name} matches to add.")


def fit_ai_models():
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
    joblib.dump(model_home, 'model_home_wins.pkl')
    joblib.dump(model_away, 'model_away_wins.pkl')