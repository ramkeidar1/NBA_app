import pandas as pd
from nba_api.stats.endpoints import leaguestandingsv3
from nba_api.stats.static import teams

print("Fetching current season data for all NBA teams...")

try:
    # 1. Fetch the comprehensive current season dataset
    standings = leaguestandingsv3.LeagueStandingsV3(
        league_id="00",
        season_type="Regular Season"
    )
    df_current_season = standings.get_data_frames()[0]
    
    # 2. Build a mapping dictionary from the static utilities (e.g., {1610612747: 'LAL'})
    nba_teams_static = teams.get_teams()
    team_abbrev_map = {team['id']: team['abbreviation'] for team in nba_teams_static}
    
    # 3. Replace the numerical TeamID column with the 3-letter abbreviations
    df_current_season['TeamID'] = df_current_season['TeamID'].map(team_abbrev_map)
    print("Successfully mapped numerical TeamIDs to 3-letter abbreviations!")

    # 4. Remove LeagueID and SeasonID columns (handles multiple casing variations safely)
    cols_to_drop = ['LeagueID', 'SeasonID', 'LEAGUE_ID', 'SEASON_ID']
    df_current_season = df_current_season.drop(columns=cols_to_drop, errors='ignore')
    print("Successfully removed LeagueID and SeasonID metadata columns!")

    # 5. Save the final clean table to a CSV file
    output_file = 'nba_current_season_clean.csv'
    df_current_season.to_csv(output_file, index=False)
    
    print("\n" + "="*60)
    print(f"SUCCESS: Exported clean data to '{output_file}'")
    print("="*60)
    
    # Display a quick preview to confirm the structural changes
    preview_cols = ['TeamID', 'TeamCity', 'TeamName', 'PlayoffRank', 'WINS', 'LOSSES']
    # Filter preview columns to only those that exist in the dataframe to prevent key errors
    preview_cols = [col for col in preview_cols if col in df_current_season.columns]
    
    print("\nData Preview (Notice no LeagueID or SeasonID columns exist):")
    print(df_current_season[preview_cols].head())

except Exception as e:
    print(f"An unexpected error occurred: {e}")