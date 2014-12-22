import numpy as np 
import itertools as it
import csv as csv

PATH_TO_DATA = '../data/'

seasons = ['2007_2008', '2008_2009', '2009_2010', '2010_2011',\
           '2011_2012', '2012_2013', '2013_2014', '2014_2015']
    
LAST_SEASON = len(seasons)
MDS_PER_SEASON = 38
MATCHES_PER_MD = 10
CURRENT_MD = 17

teams = ['Arsenal','Aston Villa','Birmingham City','Blackburn Rovers',\
         'Blackpool','Bolton Wanderers','Burnley','Cardiff City','Chelsea',\
         'Crystal Palace','Everton','Fulham','Hull City','Leicester City',\
         'Liverpool','Manchester City','Manchester United','Newcastle United',\
         'Norwich City','Queens Park Rangers','Portsmouth','Reading',\
         'Southampton','Stoke City','Sunderland','Swansea City',\
         'Tottenham Hotspur','West Bromwich Albion','West Ham United',\
         'Wigan Athletic','Wolverhampton Wanderers']

def name_to_idx(team_name):
	return teams.index(team_name)

def idx_to_name(team_idx):
	return teams[team_idx]

#Read the csv files

seasons_history = []

for season in seasons:
	csv_file_object = csv.reader(open( PATH_TO_DATA + 'matches' + season + '.csv', 'rb')) 	
	data=[] 	

	for row in csv_file_object: 							
		if(row != []):
			data.append(row[3:])	

	data = np.array(data)
	seasons_history.append(data)								

seasons_history = np.array(seasons_history)

#Transform elements to integers 

npint = np.vectorize(int)

seasons_history = npint(seasons_history)

#Replace game dates by MD numbers

seasons_history_new = np.zeros([LAST_SEASON, MDS_PER_SEASON * MATCHES_PER_MD, 5])

for season in xrange(LAST_SEASON):
	for matchday in xrange(MDS_PER_SEASON):
		for match in xrange(MATCHES_PER_MD):
			seasons_history_new[season,  MATCHES_PER_MD * matchday +  match, :] = \
			np.insert(seasons_history[season, MATCHES_PER_MD * matchday +  match, :], 0, matchday + 1, 0)

seasons_history = seasons_history_new

print(seasons_history)

# print(seasons_history_new[1])
# def find_prev_matches(team1, team2):
	
# 	matches = []

# 	for season in 



