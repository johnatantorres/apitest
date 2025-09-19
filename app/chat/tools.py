import asyncio
import httpx
import os
from langchain.tools import StructuredTool
from dotenv import load_dotenv
from datetime import datetime
from typing import Any, Dict, List
from app.chat.schemas import FixtureInput, FixtureInputDate, FixtureInputDates, FixtureInputTeam, Preferences

load_dotenv()
QUERY_API_URL = os.getenv("QUERY_API_URL")

async def fixture_parameters_request():
    url = f"{QUERY_API_URL}/sports/sports-fixtures"

    params = {
        "sportId": Preferences.sport_id,
        "type": "pre_match",
        "time_zone": "UTC",
        "language": "en"
    }

    headers = {
        "accept": "application/json"
    }

    return url, params, headers

async def get_fixtures_by_teams(team_1: str, team_2: str) -> List[Dict[str, Any]]:
    """get sports fixtures data for specified teams"""

    url, params, headers = await fixture_parameters_request()

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        selected_fixtures = [
            fixture for fixture in response.json()
            if {fixture.get("home_team_data", {}).get("name", {}).get("en"),
                fixture.get("away_team_data", {}).get("name", {}).get("en")} == {team_1, team_2}
        ]
                
        return selected_fixtures
    
def get_fixtures_by_teams_sync(team_1: str, team_2: str) -> List[Dict[str, Any]]:
    return asyncio.run(get_fixtures_by_teams(team_1, team_2))

async def get_fixtures_by_team(team: str) -> List[Dict[str, Any]]:
    """get sports fixtures data for one specified team"""

    url, params, headers = await fixture_parameters_request()

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        selected_fixtures = [
            fixture for fixture in response.json()
            if team in {fixture.get("home_team_data", {}).get("name", {}).get("en"),
                        fixture.get("away_team_data", {}).get("name", {}).get("en")}
        ]

        return selected_fixtures
    
def get_fixtures_by_team_sync(team: str) -> List[Dict[str, Any]]:
    return asyncio.run(get_fixtures_by_team(team))

def get_fixture_datestamp(fixture) -> datetime:
    str_date_time = fixture.get("startTime")
    date_time = datetime.strptime(str_date_time, "%m-%d %H:%M")
    return date_time.replace(year=datetime.now().year)

def get_fixture_date(fixture) -> str:
    return get_fixture_datestamp(fixture).strftime("%Y-%m-%d")

async def get_fixtures_by_date(date: str) -> List[Dict[str, Any]]:
    """get sports fixtures data for one specified date"""

    url = f"{QUERY_API_URL}/sports/sports-fixtures"

    params = {
        "sportId": Preferences.sport_id,
        "type": "pre_match",
        "time_zone": "UTC",
        "language": "en"
    }

    headers = {
        "accept": "application/json"
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        selected_fixtures =[
            fixture for fixture in response.json()
            if get_fixture_date(fixture) == date
        ]

        return selected_fixtures

def get_fixtures_by_date_sync(date: str) -> str:
    return asyncio.run(get_fixtures_by_date(date))

async def get_fixtures_by_dates(date_1, date_2) -> List[Dict[str, Any]]:
    """get sports fixtures data within specified date range"""
    date_1_obj = datetime.strptime(date_1, "%Y-%m-%d")
    date_2_obj = datetime.strptime(date_2, "%Y-%m-%d")
    
    url, params, headers = await fixture_parameters_request()

    selected_fixtures = []
    async with httpx.AsyncClient(timeout=30.0) as client:

        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        all_fixtures = response.json()
        selected_fixtures = [
            fixture for fixture in all_fixtures
            if date_1_obj <= get_fixture_datestamp(fixture) <= date_2_obj
        ]

    return selected_fixtures
    
def get_fixtures_by_dates_sync(date_1, date_2) -> List[Dict[str, Any]]:
    return asyncio.run(get_fixtures_by_dates(date_1, date_2))

def condense_betting_json(data):
    """
    Condense betting JSON by removing null values and redundant structures.
    """
    
    def remove_nulls_and_redundant(obj):
        """Remove null values and redundant structures"""
        if isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                if value is not None:
                    cleaned_value = remove_nulls_and_redundant(value)
                    if cleaned_value is not None and cleaned_value != {}:
                        result[key] = cleaned_value
            return result if result else None
        elif isinstance(obj, list):
            result = [remove_nulls_and_redundant(item) for item in obj if item is not None]
            return [item for item in result if item is not None and item != {}]
        else:
            return obj
    
    def simplify_bet_structure(bet_data):
        """Simplify bet structure to essential fields"""
        if not isinstance(bet_data, dict):
            return bet_data
            
        simplified = {}
        for key, value in bet_data.items():
            if isinstance(value, dict) and 'name' in value and 'odds' in value:
                # if profit equals odds, we can omit profit
                if value.get('profit') == value.get('odds'):
                    simplified[key] = {
                        'name': value['name'],
                        'odds': value['odds'],
                        'betId': value['betId']
                    }
                else:
                    simplified[key] = value
            else:
                simplified[key] = simplify_bet_structure(value)
        
        return simplified
    
    # Clean null values
    cleaned = remove_nulls_and_redundant(data)
    
    # Simplify bet structure
    condensed = simplify_bet_structure(cleaned)
    
    return condensed


async def _fetch_single_odd(client: httpx.AsyncClient, fixture: Dict[str, Any]) -> Dict[str, Any] | None:
    """Helper coroutine to fetch odds for a single fixture concurrently."""
    fixture_id = fixture.get("id")
    
    sports_id = Preferences.sport_id
    tournament_id = fixture.get("tournament_id")
    amount = 1

    url = f"{QUERY_API_URL}/sports/odds"
    params = {
        "sportId": sports_id,
        "fixtureId": fixture_id,
        "tournamentId": tournament_id,
        "amount": amount
    }
    headers = {"accept": "application/json"}

    try:
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return condense_betting_json(response.json())
    except httpx.ReadTimeout:
        print(f"[{datetime.now()}] Timeout fetching odds for fixture ID: {fixture_id}")
        return None
    except httpx.HTTPStatusError as e:
        print(f"[{datetime.now()}] HTTP error for fixture ID {fixture_id}: {e}")
        return None


async def get_odds(fixtures: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Fetch odds for a list of fixtures concurrently."""
    print(f"[{datetime.now()}] --- Starting get_odds for {len(fixtures)} fixtures ---")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        tasks = [_fetch_single_odd(client, f) for f in fixtures]
        results = await asyncio.gather(*tasks)
        odds = [r for r in results if r is not None]

    return odds

async def check_odds_by_teams(team_1: str, team_2: str) -> List[Dict[str, Any]]:
    """get betting odds for specified teams"""
    fixtures = await get_fixtures_by_teams(team_1, team_2)
                
    return await get_odds(fixtures)

def check_odds_by_teams_sync(team_1: str, team_2: str) -> List[Dict[str, Any]]:
    return asyncio.run(check_odds_by_teams(team_1, team_2))

async def check_odds_by_date(date: str) -> List[Dict[str, Any]]:
    """get betting odds for specified date"""
    fixtures = await get_fixtures_by_date(date)
                    
    return await get_odds(fixtures)

def check_odds_by_date_sync(date: str) -> List[Dict[str, Any]]:
    return asyncio.run(check_odds_by_date(date))

async def check_odds_by_dates(date_1: str, date_2: str) -> List[Dict[str, Any]]:
    """get betting odds within specified date range"""
    fixtures = await get_fixtures_by_dates(date_1, date_2)
    
    if not fixtures:
        print("No fixtures found for the given dates.")
        return []
                        
    return await get_odds(fixtures)

def check_odds_by_dates_sync(date_1: str, date_2: str) -> List[Dict[str, Any]]:
    return asyncio.run(check_odds_by_dates(date_1, date_2))

async def _initialize_tools():
    return [StructuredTool.from_function(
            name="get_fixtures_by_teams",
            func=get_fixtures_by_teams_sync,
            description="Get sports fixtures data",
            arg_schema=FixtureInput,
            coroutine=get_fixtures_by_teams
            ),

            StructuredTool.from_function(
                name="get_fixtures_by_team",
                func=get_fixtures_by_team_sync,
                description="Get sports fixtures data for one specified team",
                arg_schema=FixtureInputTeam,
                coroutine=get_fixtures_by_team
            ),
            
            StructuredTool.from_function(
                name="get_fixtures_by_date",
                func=get_fixtures_by_date_sync,
                description="Get sports fixtures data for one specified date",
                arg_schema=FixtureInputDate,
                coroutine=get_fixtures_by_date
            ),

            StructuredTool.from_function(
                name="get_fixtures_by_dates",
                func=get_fixtures_by_dates_sync,
                description="Get sports fixtures data within specified date range",
                arg_schema=FixtureInputDates,
                coroutine=get_fixtures_by_dates
            ),

            StructuredTool.from_function(
                name="check_odds_by_teams",
                func=check_odds_by_teams_sync,
                description="Get betting odds for specified teams",
                arg_schema=FixtureInput,
                coroutine=check_odds_by_teams
            ),

            StructuredTool.from_function(
                name="check_odds_by_date",
                func=check_odds_by_date_sync,
                description="Get betting odds for specified date",
                arg_schema=FixtureInputDate,
                coroutine=check_odds_by_date
            ),

            StructuredTool.from_function(
                name="check_odds_by_dates",
                func=check_odds_by_dates_sync,
                description="Get betting odds within specified date range",
                arg_schema=FixtureInputDates,
                coroutine=check_odds_by_dates
            )
        ]