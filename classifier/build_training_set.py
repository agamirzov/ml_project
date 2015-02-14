import numpy as np
import pandas as pd

PATH_TO_DATA = '../data/'

seasons = ['2007_2008', '2008_2009', '2009_2010', '2010_2011',\
           '2011_2012', '2012_2013', '2013_2014', '2014_2015']

NUM_TEAMS = 20
NUM_SEASONS = len(seasons)
SEASONS_TO_CONSIDER = 2
MDS_PER_SEASON = 38
MATCHES_PER_MD = 10
MATCHES_PER_SEASON = MDS_PER_SEASON * MATCHES_PER_MD
CURRENT_MD = 17

def match_file_name(season):
    """Generates the name of the file containing the match data for season"""
    return PATH_TO_DATA + 'matches' + season + '.csv'

def standing_file_name(season):
    """Generates the name of the file containing the match data for season"""
    return PATH_TO_DATA + 'tables' + season + '.csv'    


#Read the csv files
match_history = []
standings_history = []

for season in seasons:
    match_history.append(pd.read_csv(match_file_name(season)))
    standings_history.append(pd.read_csv(standing_file_name(season)))

def get_standing(team, season, match_day):
    """Determines team's standing on the previous match day

    If it's the first day of the season, standing from the last day of the last season is used
    If the team hasn't played last season, lowest possible place (20) is returned
    """

    standing = -1

    #Check if the team is participating in the season #season
    if standings_history[season].loc[standings_history[season]['team'] == team].empty:
        print("Team doesn't participate in the current season!")
        return standing

    #Check if it is the first day of the season
    if match_day == 1:
        standing = standings_history[season - 1].loc[standings_history[season - 1]['match_day'] == MDS_PER_SEASON].\
                    loc[standings_history[season - 1]['team'] == team]['standing']
        
        #if the team hasn't played last season
        if standing.empty:
            standing = 20
        else:
            standing = int(standing)
    else:
        standing = standings_history[season].loc[standings_history[season]['match_day'] == (match_day - 1)].\
                    loc[standings_history[season]['team'] == team]['standing']
        standing = int(standing)

    return standing

def is_team_home(team, season, match_day):
    """Return 1 if the team is playing home at the match_day of season, 0 if away

    Returns -1 if the team doesn't play on the match_day of the season
    """

    match = match_history[season].loc[match_history[season]['match_day'] == match_day]

    if not match.loc[match_history[season]['team1'] == team].empty:
        result = 1
    elif not match.loc[match_history[season]['team2'] == team].empty:
        result = 0
    else:
        print("Team %d doesn't play on md %d of season %d" %(team, match_day, season))
        result = -1

    return result