from flask import Flask, render_template, request
import requests
import os
import time
import json
from datetime import datetime, timedelta

app = Flask(__name__)

# API URLs
API_BASE = "https://api.football-data.org/v4"
API_URL = f"{API_BASE}/competitions"
MATCHES_URL = f"{API_BASE}/matches"
API_KEY = os.environ.get("FOOTBALL_API_KEY")  # Set this on each server

# Fallback data for when API is rate limited
FALLBACK_COMPETITIONS = [
    {"name": "Premier League", "code": "PL", "area": {"name": "England"}, "plan": "TIER_ONE"},
    {"name": "La Liga", "code": "PD", "area": {"name": "Spain"}, "plan": "TIER_ONE"},
    {"name": "Bundesliga", "code": "BL1", "area": {"name": "Germany"}, "plan": "TIER_ONE"},
    {"name": "Serie A", "code": "SA", "area": {"name": "Italy"}, "plan": "TIER_ONE"},
    {"name": "Ligue 1", "code": "FL1", "area": {"name": "France"}, "plan": "TIER_ONE"},
    {"name": "Eredivisie", "code": "DED", "area": {"name": "Netherlands"}, "plan": "TIER_ONE"},
    {"name": "Primeira Liga", "code": "PPL", "area": {"name": "Portugal"}, "plan": "TIER_ONE"},
    {"name": "Championship", "code": "ELC", "area": {"name": "England"}, "plan": "TIER_TWO"},
    {"name": "UEFA Champions League", "code": "CL", "area": {"name": "Europe"}, "plan": "TIER_ONE"},
    {"name": "FIFA World Cup", "code": "WC", "area": {"name": "World"}, "plan": "TIER_ONE"},
    {"name": "Campeonato Brasileiro Série A", "code": "BSA", "area": {"name": "Brazil"}, "plan": "TIER_ONE"},
    {"name": "Copa Libertadores", "code": "CLI", "area": {"name": "South America"}, "plan": "TIER_ONE"},
    {"name": "European Championship", "code": "EC", "area": {"name": "Europe"}, "plan": "TIER_ONE"}
]

# Sample live matches (fallback data)
FALLBACK_MATCHES = [
    {
        "homeTeam": {"name": "Manchester United", "crest": "🔴"}, 
        "awayTeam": {"name": "Liverpool", "crest": "🔴"},
        "utcDate": (datetime.now() + timedelta(hours=2)).isoformat(),
        "status": "SCHEDULED",
        "competition": {"name": "Premier League"},
        "score": {"fullTime": {"home": None, "away": None}}
    },
    {
        "homeTeam": {"name": "Barcelona", "crest": "🔵"}, 
        "awayTeam": {"name": "Real Madrid", "crest": "⚪"},
        "utcDate": datetime.now().isoformat(),
        "status": "IN_PLAY",
        "competition": {"name": "La Liga"},
        "score": {"fullTime": {"home": 2, "away": 1}}
    },
    {
        "homeTeam": {"name": "Bayern Munich", "crest": "🔴"}, 
        "awayTeam": {"name": "Borussia Dortmund", "crest": "🟡"},
        "utcDate": (datetime.now() - timedelta(hours=1)).isoformat(),
        "status": "FINISHED",
        "competition": {"name": "Bundesliga"},
        "score": {"fullTime": {"home": 3, "away": 2}}
    }
]

# Cache for API responses
api_cache = {"data": None, "timestamp": 0}
CACHE_DURATION = 300  # 5 minutes

def get_competitions_data():
    """Get competitions data from API or fallback"""
    global api_cache
    current_time = time.time()
    
    # Use cached data if available and fresh
    if api_cache["data"] and (current_time - api_cache["timestamp"]) < CACHE_DURATION:
        return api_cache["data"], False
    
    try:
        headers = {"X-Auth-Token": API_KEY} if API_KEY else {}
        response = requests.get(API_URL, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            competitions = data.get("competitions", [])
            api_cache["data"] = competitions
            api_cache["timestamp"] = current_time
            return competitions, False
        else:
            # API error, use fallback
            return FALLBACK_COMPETITIONS, True
    except Exception:
        # Connection error, use fallback
        return FALLBACK_COMPETITIONS, True

def get_live_matches():
    """Get today's live matches from API or fallback"""
    try:
        if not API_KEY:
            return FALLBACK_MATCHES, True
            
        headers = {"X-Auth-Token": API_KEY}
        today = datetime.now().strftime('%Y-%m-%d')
        params = {'dateFrom': today, 'dateTo': today}
        
        response = requests.get(MATCHES_URL, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            matches = data.get("matches", [])
            return matches[:10], False  # Limit to 10 matches
        else:
            return FALLBACK_MATCHES, True
    except Exception:
        return FALLBACK_MATCHES, True

def get_upcoming_matches():
    """Get upcoming matches for next 7 days (simple version for beginners)"""
    # Simple upcoming matches data (beginner approach)
    upcoming = [
        {
            "homeTeam": {"name": "Chelsea"}, 
            "awayTeam": {"name": "Arsenal"},
            "utcDate": (datetime.now() + timedelta(days=1)).isoformat(),
            "status": "SCHEDULED",
            "competition": {"name": "Premier League"},
            "score": {"fullTime": {"home": None, "away": None}}
        },
        {
            "homeTeam": {"name": "AC Milan"}, 
            "awayTeam": {"name": "Inter Milan"},
            "utcDate": (datetime.now() + timedelta(days=2)).isoformat(),
            "status": "SCHEDULED",
            "competition": {"name": "Serie A"},
            "score": {"fullTime": {"home": None, "away": None}}
        },
        {
            "homeTeam": {"name": "Paris Saint-Germain"}, 
            "awayTeam": {"name": "Marseille"},
            "utcDate": (datetime.now() + timedelta(days=3)).isoformat(),
            "status": "SCHEDULED",
            "competition": {"name": "Ligue 1"},
            "score": {"fullTime": {"home": None, "away": None}}
        }
    ]
    
    try:
        if API_KEY:
            # Try to get real upcoming matches
            headers = {"X-Auth-Token": API_KEY}
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            week_ahead = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            params = {'dateFrom': tomorrow, 'dateTo': week_ahead}
            
            response = requests.get(MATCHES_URL, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                real_matches = data.get("matches", [])
                if real_matches:
                    return real_matches[:5], False  # Return first 5 real matches
        
        # Fallback to simple data
        return upcoming, True
        
    except Exception:
        return upcoming, True

def format_match_time(utc_date_str):
    """Format match time for display"""
    try:
        utc_time = datetime.fromisoformat(utc_date_str.replace('Z', '+00:00'))
        return utc_time.strftime('%H:%M')
    except:
        return "TBD"

def format_upcoming_date(utc_date_str):
    """Format upcoming match date (simple version for beginners)"""
    try:
        utc_time = datetime.fromisoformat(utc_date_str.replace('Z', '+00:00'))
        return utc_time.strftime('%B %d, %Y')  # Example: January 23, 2025
    except:
        return "Date TBD"

def get_match_status_display(status):
    """Get friendly status display"""
    status_map = {
        'SCHEDULED': ' Scheduled',
        'IN_PLAY': ' LIVE',
        'PAUSED': ' Half Time', 
        'FINISHED': ' Finished',
        'POSTPONED': ' Postponed',
        'CANCELLED': ' Cancelled'
    }
    return status_map.get(status, status)

@app.route("/")
def home():
    try:
        # Get query parameters
        search_query = request.args.get('search', '').lower()
        sort_by = request.args.get('sort', 'name')
        filter_country = request.args.get('country', '')
        
        # Get competitions data
        competitions, using_fallback = get_competitions_data()
        
        # Get live matches
        live_matches, matches_fallback = get_live_matches()
        
        # Get upcoming matches (simple feature for beginners)
        upcoming_matches, upcoming_fallback = get_upcoming_matches()
        
        # Process live matches for display
        processed_matches = []
        for match in live_matches:
            processed_match = {
                'homeTeam': match.get('homeTeam', {}).get('name', 'Unknown'),
                'awayTeam': match.get('awayTeam', {}).get('name', 'Unknown'),
                'homeScore': match.get('score', {}).get('fullTime', {}).get('home'),
                'awayScore': match.get('score', {}).get('fullTime', {}).get('away'),
                'status': get_match_status_display(match.get('status', 'UNKNOWN')),
                'competition': match.get('competition', {}).get('name', 'Unknown'),
                'time': format_match_time(match.get('utcDate', '')),
                'is_live': match.get('status') == 'IN_PLAY'
            }
            processed_matches.append(processed_match)
        
        # Process upcoming matches for display (simple approach)
        processed_upcoming = []
        for match in upcoming_matches:
            upcoming_match = {
                'homeTeam': match.get('homeTeam', {}).get('name', 'Unknown'),
                'awayTeam': match.get('awayTeam', {}).get('name', 'Unknown'),
                'competition': match.get('competition', {}).get('name', 'Unknown'),
                'date': format_upcoming_date(match.get('utcDate', '')),
                'time': format_match_time(match.get('utcDate', ''))
            }
            processed_upcoming.append(upcoming_match)
        
        # Filter by search query
        if search_query:
            competitions = [comp for comp in competitions 
                          if search_query in comp.get('name', '').lower() 
                          or search_query in comp.get('code', '').lower()]
        
        # Filter by country
        if filter_country:
            competitions = [comp for comp in competitions 
                          if comp.get('area', {}).get('name', '').lower() == filter_country.lower()]
        
        # Sort competitions
        if sort_by == 'name':
            competitions.sort(key=lambda x: x.get('name', ''))
        elif sort_by == 'country':
            competitions.sort(key=lambda x: x.get('area', {}).get('name', ''))
        
        # Get unique countries for filter dropdown (from all available data)
        all_competitions = get_competitions_data()[0]  # Get all competitions for countries list
        countries = sorted(list(set([comp.get('area', {}).get('name', '') 
                                   for comp in all_competitions 
                                   if comp.get('area', {}).get('name')])))
        
        # Prepare status message
        status_message = None
        if using_fallback:
            status_message = " Using sample data - Live API data will load when available."
        
        return render_template("index.html", 
                             competitions=competitions, 
                             countries=countries,
                             current_search=request.args.get('search', ''),
                             current_sort=sort_by,
                             current_country=filter_country,
                             status_message=status_message,
                             live_matches=processed_matches,
                             upcoming_matches=processed_upcoming)
                             
    except Exception as e:
        # Fallback to sample data with error message
        error_message = "Unable to load data. Showing sample competitions."
        
        return render_template("index.html", 
                             competitions=FALLBACK_COMPETITIONS[:5], 
                             countries=["England", "Spain", "Germany", "Italy", "France"],
                             current_search=request.args.get('search', ''),
                             current_sort=request.args.get('sort', 'name'),
                             current_country=request.args.get('country', ''),
                             error_message=error_message)

# Competition teams data (simple approach for beginners)
def get_competition_teams(competition_name):
    """Get teams for a specific competition (simple version)"""
    # Simple teams database by competition
    competition_teams = {
        "premier league": [
            {"name": "Arsenal", "stadium": "Emirates Stadium", "founded": "1886"},
            {"name": "Chelsea", "stadium": "Stamford Bridge", "founded": "1905"},
            {"name": "Liverpool", "stadium": "Anfield", "founded": "1892"},
            {"name": "Manchester United", "stadium": "Old Trafford", "founded": "1878"},
            {"name": "Manchester City", "stadium": "Etihad Stadium", "founded": "1880"},
            {"name": "Tottenham", "stadium": "Tottenham Hotspur Stadium", "founded": "1882"}
        ],
        "la liga": [
            {"name": "Real Madrid", "stadium": "Santiago Bernabéu", "founded": "1902"},
            {"name": "Barcelona", "stadium": "Camp Nou", "founded": "1899"},
            {"name": "Atletico Madrid", "stadium": "Wanda Metropolitano", "founded": "1903"},
            {"name": "Sevilla", "stadium": "Ramón Sánchez Pizjuán", "founded": "1890"},
            {"name": "Valencia", "stadium": "Mestalla", "founded": "1919"},
            {"name": "Real Sociedad", "stadium": "Reale Arena", "founded": "1909"}
        ],
        "bundesliga": [
            {"name": "Bayern Munich", "stadium": "Allianz Arena", "founded": "1900"},
            {"name": "Borussia Dortmund", "stadium": "Signal Iduna Park", "founded": "1909"},
            {"name": "RB Leipzig", "stadium": "Red Bull Arena", "founded": "2009"},
            {"name": "Bayer Leverkusen", "stadium": "BayArena", "founded": "1904"},
            {"name": "Eintracht Frankfurt", "stadium": "Deutsche Bank Park", "founded": "1899"},
            {"name": "Borussia Mönchengladbach", "stadium": "Borussia-Park", "founded": "1900"}
        ],
        "serie a": [
            {"name": "Juventus", "stadium": "Allianz Stadium", "founded": "1897"},
            {"name": "AC Milan", "stadium": "San Siro", "founded": "1899"},
            {"name": "Inter Milan", "stadium": "San Siro", "founded": "1908"},
            {"name": "AS Roma", "stadium": "Stadio Olimpico", "founded": "1927"},
            {"name": "Napoli", "stadium": "Stadio Diego Armando Maradona", "founded": "1926"},
            {"name": "Lazio", "stadium": "Stadio Olimpico", "founded": "1900"}
        ],
        "ligue 1": [
            {"name": "Paris Saint-Germain", "stadium": "Parc des Princes", "founded": "1970"},
            {"name": "Marseille", "stadium": "Stade Vélodrome", "founded": "1899"},
            {"name": "Lyon", "stadium": "Groupama Stadium", "founded": "1950"},
            {"name": "Monaco", "stadium": "Stade Louis II", "founded": "1924"},
            {"name": "Nice", "stadium": "Allianz Riviera", "founded": "1904"},
            {"name": "Lille", "stadium": "Stade Pierre-Mauroy", "founded": "1944"}
        ]
    }
    
    # Simple search (beginner approach)
    comp_key = competition_name.lower()
    return competition_teams.get(comp_key, [])

@app.route("/competition/<competition_name>")
def competition_details(competition_name):
    """Show competition details with teams (simple version)"""
    teams = get_competition_teams(competition_name)
    
    # Format competition name for display
    display_name = competition_name.replace("-", " ").title()
    
    if teams:
        return render_template("competition.html", 
                             competition_name=display_name, 
                             teams=teams)
    else:
        return render_template("competition.html", 
                             competition_name=display_name, 
                             teams=None)

# Simple team information (beginner-friendly approach)
def get_team_info(team_name):
    """Get basic team information (simple version for beginners)"""
    # Simple team database (beginner approach)
    teams = {
        "manchester united": {
            "name": "Manchester United",
            "country": "England",
            "league": "Premier League",
            "stadium": "Old Trafford",
            "founded": "1878",
            "colors": "Red, White",
            "nickname": "The Red Devils"
        },
        "barcelona": {
            "name": "FC Barcelona",
            "country": "Spain",
            "league": "La Liga",
            "stadium": "Camp Nou",
            "founded": "1899",
            "colors": "Blue, Red",
            "nickname": "Barça"
        },
        "real madrid": {
            "name": "Real Madrid",
            "country": "Spain",
            "league": "La Liga",
            "stadium": "Santiago Bernabéu",
            "founded": "1902",
            "colors": "White",
            "nickname": "Los Blancos"
        },
        "bayern munich": {
            "name": "FC Bayern Munich",
            "country": "Germany",
            "league": "Bundesliga",
            "stadium": "Allianz Arena",
            "founded": "1900",
            "colors": "Red, White",
            "nickname": "Die Bayern"
        },
        "liverpool": {
            "name": "Liverpool FC",
            "country": "England",
            "league": "Premier League",
            "stadium": "Anfield",
            "founded": "1892",
            "colors": "Red",
            "nickname": "The Reds"
        }
    }
    
    # Simple search (beginner approach)
    team_key = team_name.lower()
    return teams.get(team_key, None)

@app.route("/team/<team_name>")
def team_details(team_name):
    """Show team details page (simple version)"""
    team_info = get_team_info(team_name)
    
    if team_info:
        return render_template("team.html", team=team_info)
    else:
        return render_template("team.html", team=None, team_name=team_name)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5001, help='Port to run the server on')
    args = parser.parse_args()
    
    app.run(host="0.0.0.0", port=args.port)
