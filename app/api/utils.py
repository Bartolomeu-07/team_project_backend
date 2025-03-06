import random

import requests
from random import choices, uniform

from .models import Country, Competition, Match, Team

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
                new_competitions.append(Competition(competition_id=competition_id, name=name, country=country))
        if new_competitions:
            Competition.objects.bulk_create(new_competitions)
            print(f"{len(new_competitions)} new competitions created.")
        else:
            print("No new competitions to add.")
    else:
        print("Error during fetching competitions:", response.status_code)


def fetch_and_create_teams():
    competitions_to_create = [135, 61, 78, 2, 140, 39]

    for competition_id in competitions_to_create:
        params = {
            'league': competition_id,
            'season': '2023'
        }

        response = requests.get(url + 'teams', headers=HEADERS, params=params)
        if response.status_code == 200:
            data = response.json().get('response', [])
            league = Competition.objects.get(competition_id=params.get('league'))
            countries = Country.objects.all()
            existing_teams_ids = set(Team.objects.values_list('team_id', flat=True))
            new_teams = []

            for item in data:
                team_data = item.get('team', {})
                team_id = team_data.get('id')

                if team_id and team_id not in existing_teams_ids:
                    code = team_data.get('code')
                    name = team_data.get('name')
                    country_name = team_data.get('country')
                    try:
                        country = countries.get(name=country_name)
                    except:
                        country = None
                    logo = team_data.get('logo')
                    new_teams.append(Team(team_id=team_id,
                                                 code=code,
                                                 name=name,
                                                 league=league,
                                                 country=country,
                                                 logo=logo))
                    existing_teams_ids.add(team_id)
            if new_teams:
                Team.objects.bulk_create(new_teams)
                print(f"{len(new_teams)} new teams created.")
            else:
                print(f"No new teams to add.")
        else:
            print("Error during fetching teams:", response.status_code)


def create_or_update_match_data():
    competitions_to_update = [135, 61, 78, 2, 140, 39]


    for competition_id in competitions_to_update:
        params = {
            'league': competition_id,
            'season': '2023',
        }

        response = requests.get(url + 'fixtures', headers=HEADERS, params=params)
        if response.status_code == 200:
            data = response.json().get('response', [])
            existing_matches = Match.objects.filter(competition_id=params.get('league'))
            existing_matches_ids = set(existing_matches.values_list('match_id', flat=True))
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
                    home_team_last_five_results = random.choices(['W', 'D', 'L'], k=5)
                    away_team_last_five_results = random.choices(['W', 'D', 'L'], k=5)
                    home_score = item.get('goals').get('home')
                    away_score = item.get('goals').get('away')
                    home_wins_probability = round(uniform(-1, 1), 2)
                    away_wins_probability = round(uniform(-1, 1), 2)
                    date = item.get('fixture').get('date')
                    status = item.get('fixture').get('status').get('long')

                    new_matches.append(Match(match_id=match_id,
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
                                             ))
            if new_matches:
                Match.objects.bulk_create(new_matches)
                print(f"{len(new_matches)} new {competition.name} matches created.")
            else:
                print(f"No new {competition.name} matches to add.")
        else:
            print("Error during fetching matches:", response.status_code)


