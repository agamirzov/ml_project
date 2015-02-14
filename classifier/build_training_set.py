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


